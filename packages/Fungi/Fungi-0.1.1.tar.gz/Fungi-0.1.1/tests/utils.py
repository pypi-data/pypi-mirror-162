from contextlib import contextmanager
from multiprocessing import Process
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Callable, Generator, Iterable, Optional


@contextmanager
def process(target: Callable, *args, **kwargs) -> Generator[None, None, None]:
    proc = Process(target=target, args=args, kwargs=kwargs)
    try:
        proc.start()
        sleep(0.2)
        yield None
    finally:
        proc.terminate()
        proc.join(10)
        if not proc.exitcode:
            proc.kill()
            proc.join()


@contextmanager
def temp_dir(paths: Optional[Iterable[str]] = None) -> Generator[Path, None, None]:
    with TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        if paths:
            for path in paths:
                if path.endswith('/'):
                    (tmp / path[:-1]).mkdir(exist_ok=True, parents=True)
                else:
                    (tmp / path).parent.mkdir(exist_ok=True, parents=True)
                    (tmp / path).touch()
        yield tmp
