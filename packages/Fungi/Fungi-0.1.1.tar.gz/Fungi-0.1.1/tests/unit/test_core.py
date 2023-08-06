from os import utime
from pathlib import Path
from shutil import rmtree
from time import sleep, time
from typing import Tuple, List

from fungi.core import Monitor, MODIFIED_OR_DELETED, Changed, Flags, MemoryMonitor
from fungi.core import SymlinkMonitor, SQLiteMonitor, _is_child, open_for_writing
from ..utils import process, temp_dir


def test_is_child() -> None:
    path_a = Path.cwd()
    path_b = Path.cwd().parent
    assert _is_child(path_a, path_b)
    assert not _is_child(path_b, path_a)


def test_open_for_writing_file() -> None:
    with temp_dir() as tmp:
        stuff = tmp / 'stuff.txt'
        with stuff.open('w+') as to_write:
            to_write.write('stuff')
            assert open_for_writing(stuff)
            assert open_for_writing(tmp)
            to_write.write('more stuff')
        assert not open_for_writing(stuff)
    assert not open_for_writing(stuff)


def test_basic_inotify():
    with temp_dir() as tmp:
        observed = tmp / 'observe'
        observed.mkdir()

        def change_stuff():
            sleep(0.4)
            (observed / 'stuff.txt').touch()
            (observed / 'stuff').mkdir()
            (observed / 'stuff' / 'stuff.txt').touch()
            (observed / 'stuff.txt').touch()

        results: List[Tuple[Changed, Path]] = []
        with process(change_stuff):
            for changed in Monitor(MODIFIED_OR_DELETED, [observed]).read(timeout=1000,
                                                                         read_delay=100):
                assert changed is not None
                results.append(changed)
                if len(results) >= 3:
                    break

        assert results[0] == ([Flags.CREATE], observed / 'stuff.txt')
        assert results[1] == ([Flags.CREATE, Flags.ISDIR], observed / 'stuff')
        assert results[2] == ([Flags.ATTRIB], observed / 'stuff.txt')


def test_inotify_timeout():
    with temp_dir(['observe/']) as tmp:
        def change_stuff():
            sleep(0.4)
            (tmp / 'observe' / 'stuff.txt').touch()
            sleep(0.4)
            (tmp / 'observe' / 'stuff').mkdir()

        results: List[Tuple[Changed, Path]] = []
        with process(change_stuff):
            for changed in Monitor(MODIFIED_OR_DELETED, [tmp / 'observe']).read(timeout=100,
                                                                                read_delay=100):
                results.append(changed)
                if len(results) >= 7:
                    break

        assert None in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results
        assert ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'stuff') in results


def test_fs_scan_single_dir():
    with temp_dir(['observe/']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results


def test_fs_scan_recursive_files():
    with temp_dir(['observe/', 'observe/stuff.txt']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results


def test_fs_scan_files_and_folders():
    with temp_dir(['observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                      tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe' / 'a') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_fs_scan_files_and_folders_over_time():
    with temp_dir(['observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                      tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results


def test_fs_scan_files_delete():
    with temp_dir(['observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                      tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        rmtree((tmp / 'observe' / 'a'))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.DELETE_SELF], tmp / 'observe' / 'a') in results
        assert ([Flags.DELETE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_fs_scan_files_and_folders_changed_when_not_running():
    with temp_dir(['observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = MemoryMonitor(MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                      tmp / 'observe' / 'stuff.txt'])

        def change_stuff():
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2.txt').touch()
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2').mkdir()

        results: List[Tuple[Changed, Path]] = []
        with process(change_stuff):
            for changed in monitor.read(timeout=1000, read_delay=100):
                assert changed is not None
                results.append(changed)
                if ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results:
                    break
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff2.txt') in results
        assert ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results


# ----------------------------------------------------------------------------------------
# ---------------------------------- SymlinkMonitor --------------------------------------
# ----------------------------------------------------------------------------------------

def test_symlink_mon_fs_scan_single_dir():
    with temp_dir(['.db/', 'observe/']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results


def test_symlink_mon_fs_scan_recursive_files():
    with temp_dir(['.db/', 'observe/', 'observe/stuff.txt']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results


def test_symlink_mon_fs_scan_files_and_folders():
    with temp_dir(['.db/', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                    tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe' / 'a') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_symlink_mon_fs_scan_files_and_folders_over_time():
    with temp_dir(['.db/', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                    tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results


def test_symlink_mon_fs_scan_files_delete():
    with temp_dir(['.db/', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                    tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        rmtree((tmp / 'observe' / 'a'))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.DELETE_SELF], tmp / 'observe' / 'a') in results
        assert ([Flags.DELETE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_symlink_mon_fs_scan_files_and_folders_changed_when_not_running():
    with temp_dir(['.db/', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SymlinkMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                    tmp / 'observe' / 'stuff.txt'])

        def change_stuff():
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2.txt').touch()
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2').mkdir()

        results: List[Tuple[Changed, Path]] = []
        with process(change_stuff):
            for changed in monitor.read(timeout=1000, read_delay=100):
                assert changed is not None
                results.append(changed)
                if ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results:
                    break
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff2.txt') in results
        assert ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results


# ----------------------------------------------------------------------------------------
# ---------------------------------- SQLiteMonitor ---------------------------------------
# ----------------------------------------------------------------------------------------

def test_sqlite_mon_fs_scan_single_dir():
    with temp_dir(['.db', 'observe/']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results


def test_sqlite_mon_fs_scan_recursive_files():
    with temp_dir(['.db', 'observe/', 'observe/stuff.txt']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results


def test_sqlite_mon_fs_scan_files_and_folders():
    with temp_dir(['.db', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                   tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.ISDIR, Flags.CREATE], tmp / 'observe' / 'a') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'stuff.txt') in results
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_sqlite_mon_fs_scan_files_and_folders_over_time():
    with temp_dir(['.db', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                   tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results


def test_sqlite_mon_fs_scan_files_delete():
    with temp_dir(['.db', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                   tmp / 'observe' / 'stuff.txt'])
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        rmtree((tmp / 'observe' / 'a'))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.DELETE_SELF], tmp / 'observe' / 'a') in results
        assert ([Flags.DELETE], tmp / 'observe' / 'a' / 'stuff.txt') in results


def test_sqlite_mon_fs_scan_files_and_folders_changed_when_not_running():
    with temp_dir(['.db', 'observe/stuff.txt', 'observe/a/stuff.txt']) as tmp:
        monitor = SQLiteMonitor(tmp / '.db', MODIFIED_OR_DELETED, [tmp / 'observe' / 'a',
                                                                   tmp / 'observe' / 'stuff.txt'])

        def change_stuff():
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2.txt').touch()
            sleep(0.3)
            (tmp / 'observe' / 'a' / 'stuff2').mkdir()

        results: List[Tuple[Changed, Path]] = []
        with process(change_stuff):
            for changed in monitor.read(timeout=1000, read_delay=100):
                assert changed is not None
                results.append(changed)
                if ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results:
                    break
        assert ([Flags.CREATE], tmp / 'observe' / 'a' / 'stuff2.txt') in results
        assert ([Flags.CREATE, Flags.ISDIR], tmp / 'observe' / 'a' / 'stuff2') in results
        utime((tmp / 'observe' / 'stuff.txt'), times=(time(), time()))
        results: List[Tuple[Changed, Path]] = []
        for changed in monitor.scan():
            results.append(changed)
        assert ([Flags.MODIFY], tmp / 'observe' / 'stuff.txt') in results
