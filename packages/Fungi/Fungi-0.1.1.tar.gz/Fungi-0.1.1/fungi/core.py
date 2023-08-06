from abc import ABC, abstractmethod
from collections import defaultdict
from os import readlink, symlink, utime, stat
from pathlib import Path
from sqlite3 import connect
from time import time
from typing import Tuple, Generator, List, Optional, Set, DefaultDict, Union, TypeVar
from uuid import uuid4 as uuid

from inotify_simple import INotify, flags as Flags
from psutil import process_iter, AccessDenied, NoSuchProcess


T = TypeVar("T")  # pylint: disable=C0103
Removable = Union[List[T], Set[T]]
Changed = Tuple[List[Union[Flags, int]], Path]
ChangedGenerator = Generator[Optional[Changed], None, None]


class Monitor:
    def __init__(self, flags: Union[Flags, int], paths: Removable[Path]) -> None:
        self.flags = flags
        self.paths = paths

    def read(
        self, timeout: Optional[int] = None, read_delay: Optional[int] = None
    ) -> ChangedGenerator:
        inotify = INotify()
        watches = {}
        try:
            for path in self.paths:
                watches[inotify.add_watch(str(path), self.flags)] = path
            while 42:
                for event in inotify.read(timeout=timeout, read_delay=read_delay):
                    yield (
                        Flags.from_mask(event.mask),
                        watches[event.wd] / event.name
                        if watches[event.wd].is_dir()
                        else watches[event.wd],
                    )
                yield None
        finally:
            for watch in watches:
                inotify.rm_watch(watch)
            inotify.close()


class StatefulMonitor(ABC, Monitor):
    @abstractmethod
    def update(self, path: Path) -> None:
        ...  # pragma: no cover

    def updated(self, path: Path) -> bool:
        return path.stat().st_mtime > self.last_processed(path)

    @abstractmethod
    def last_processed(self, path: Path) -> float:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def known(self) -> Set[Path]:
        ...  # pragma: no cover

    @abstractmethod
    def is_known(self, path: Path) -> bool:
        ...  # pragma: no cover

    @abstractmethod
    def forget(self, path: Path):
        ...  # pragma: no cover

    def scan(self) -> ChangedGenerator:  # pylint: disable=R0912
        unaccounted = self.known
        for path in self.paths:
            if path.is_dir():
                unaccounted.discard(path)  # path accounted for
                if self.updated(path):  # track the directory
                    try:
                        yield (
                            [
                                Flags.ISDIR,
                                (
                                    Flags.CREATE
                                    if not self.is_known(path)
                                    else Flags.MODIFY
                                ),
                            ],
                            path,
                        )
                    finally:
                        self.update(path)
                for child in path.iterdir():  # track all directory children
                    unaccounted.discard(child)
                    if self.updated(child):
                        try:
                            yield (
                                [
                                    Flags.CREATE
                                    if not self.is_known(child)
                                    else Flags.MODIFY
                                ]
                                + ([Flags.ISDIR] if child.is_dir() else []),
                                child,
                            )
                        finally:
                            self.update(child)
            elif path.is_file():
                unaccounted.discard(path)  # path accounted for
                if self.updated(path):  # track the file
                    try:
                        yield (
                            [Flags.CREATE if not self.is_known(path) else Flags.MODIFY],
                            path,
                        )
                    finally:
                        self.update(path)
        for unaccounted_path in unaccounted:
            try:
                yield (
                    [
                        Flags.DELETE
                        if unaccounted_path not in self.paths
                        else Flags.DELETE_SELF
                    ],
                    unaccounted_path,
                )
            finally:
                if unaccounted_path in self.paths:
                    self.paths.remove(unaccounted_path)
                self.forget(unaccounted_path)

    def read(
        self, timeout: Optional[int] = None, read_delay: Optional[int] = None
    ) -> ChangedGenerator:
        for scanned in self.scan():
            yield scanned
        for inotified in super().read(timeout, read_delay):  # pragma: no branch
            if inotified:
                try:
                    yield inotified
                finally:
                    self.update(inotified[1])
            else:
                for scanned in self.scan():
                    yield scanned


class MemoryMonitor(StatefulMonitor):
    def __init__(self, flags: Union[Flags, int], paths: Removable[Path]) -> None:
        self._tracked: DefaultDict[Path, float] = defaultdict(float)
        super().__init__(flags, paths)

    def update(self, path: Path) -> None:
        self._tracked[path] = time()

    def last_processed(self, path: Path) -> float:
        return self._tracked[path]

    @property
    def known(self) -> Set[Path]:
        return set(self._tracked.keys())

    def is_known(self, path: Path) -> bool:
        return self._tracked[path] != 0.0

    def forget(self, path: Path):
        del self._tracked[path]


class SQLiteMonitor(StatefulMonitor):
    def __init__(
        self, tracking_db: Path, flags: Union[Flags, int], paths: Removable[Path]
    ) -> None:
        assert tracking_db.parent.exists()
        assert tracking_db.is_file() or not tracking_db.exists()
        self.db_conn = connect(tracking_db)
        self._init_db()
        super().__init__(flags, paths)

    def _init_db(self) -> None:
        with self.db_conn:
            self.db_conn.execute(
                """CREATE TABLE IF NOT EXISTS tracked_file
                                    (path string primary key, last_updated float)"""
            )

    def update(self, path: Path) -> None:
        with self.db_conn:
            self.db_conn.execute(
                """INSERT INTO tracked_file(path,last_updated)
                                    VALUES(?, ?)
                                    ON CONFLICT(path) DO UPDATE SET
                                    last_updated=excluded.last_updated""",
                (str(path), time()),
            )

    def last_processed(self, path: Path) -> float:
        with self.db_conn:
            for row in self.db_conn.execute(
                "SELECT last_updated FROM tracked_file WHERE path=?", (str(path),)
            ):
                return float(row[0])
        return 0.0

    @property
    def known(self) -> Set[Path]:
        with self.db_conn:
            return {
                Path(row[0])
                for row in self.db_conn.execute("SELECT path from tracked_file")
            }

    def is_known(self, path: Path) -> bool:
        with self.db_conn:
            for _ in self.db_conn.execute(
                "SELECT last_updated FROM tracked_file WHERE path=?", (str(path),)
            ):
                return True
        return False

    def forget(self, path: Path):
        with self.db_conn:
            self.db_conn.execute("DELETE FROM tracked_file WHERE path=?", (str(path),))


class SymlinkMonitor(StatefulMonitor):
    def __init__(
        self, tracking_dir: Path, flags: Union[Flags, int], paths: Removable[Path]
    ) -> None:
        assert tracking_dir.is_dir()
        self.tracking_dir = tracking_dir
        super().__init__(flags, paths)

    def _symlink_for(self, path: Path) -> Optional[Path]:
        for child in self.tracking_dir.iterdir():
            if Path(readlink(child)) == path:
                return child
        return None

    def update(self, path: Path) -> None:
        link = self._symlink_for(path)
        if link:
            utime(link, times=(time(), time()), follow_symlinks=False)
        else:
            symlink(path, self.tracking_dir / str(uuid()))

    def last_processed(self, path: Path) -> float:
        link = self._symlink_for(path)
        return stat(link, follow_symlinks=False).st_mtime if link is not None else 0.0

    @property
    def known(self) -> Set[Path]:
        return set(Path(readlink(c)) for c in self.tracking_dir.iterdir())

    def is_known(self, path: Path) -> bool:
        return self._symlink_for(path) is not None

    def forget(self, path: Path):
        link = self._symlink_for(path)
        if link:  # pragma: no branch
            link.unlink()


MODIFIED_OR_DELETED = (
    Flags.MODIFY
    | Flags.ATTRIB
    | Flags.MOVED_FROM
    | Flags.MOVED_TO
    | Flags.CREATE
    | Flags.DELETE
    | Flags.DELETE_SELF
    | Flags.MOVE_SELF
)
MODIFIED = Flags.MODIFY | Flags.ATTRIB | Flags.MOVED_TO | Flags.CREATE


def _is_child(child: Path, parent: Path) -> bool:
    assert child.exists() and parent.is_dir()
    return any(par for par in child.parents if par == parent)


def open_for_writing(file_path: Path) -> bool:
    file_path.resolve()
    for proc in process_iter():
        try:
            if file_path.is_file() and any(
                pf
                for pf in proc.open_files()
                if ("w" in pf.mode or "+" in pf.mode) and pf.path == str(file_path)
            ):
                return True
            if file_path.is_dir() and any(
                pf
                for pf in proc.open_files()
                if ("w" in pf.mode or "+" in pf.mode)
                and _is_child(Path(pf.path), file_path)
            ):
                return True
        except (NoSuchProcess, AccessDenied, PermissionError):
            pass
    return False
