import asyncio
import importlib
import logging
import sys
from types import TracebackType


LOG = logging.getLogger('query')
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    formatter = logging.Formatter(f"%(levelname)8s: %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    LOG.addHandler(stream_handler)

logging.addLevelName(logging.FATAL, 'fatal')
logging.addLevelName(logging.ERROR, 'error')
logging.addLevelName(logging.WARNING, 'warning')
logging.addLevelName(logging.INFO, 'info')
logging.addLevelName(logging.DEBUG, 'debug')

def set_log_level(level: str) -> None:
    LOG.setLevel(level)
    stream_handler.setLevel(level)


class ConcurrencyLimit:
    def __init__(self, max_concurrent: int) -> None:
        self.semaphore = asyncio.BoundedSemaphore(max_concurrent)

    async def __aenter__(self) -> None:
        await self.semaphore.acquire()

    async def __aexit__(
            self, _exc_type: type[BaseException] | None, _exc_val: BaseException | None,
            _exc_tb: TracebackType | None) -> None:
        self.semaphore.release()


def resolve_imports() -> None:
    frame = sys._getframe().f_back # type: ignore[reportPrivateUsage]
    assert frame is not None
    for name in frame.f_code.co_names:
        if name not in frame.f_globals and \
                name not in frame.f_locals and \
                name not in dir(__builtins__):
            try:
                frame.f_globals[name] = importlib.import_module(name)
                LOG.debug(f'Imported {name}')
            except ModuleNotFoundError:
                pass


async def run_shell(command: str) -> None:
    LOG.debug(f'Running `{command}`')
    proc = await asyncio.create_subprocess_shell(command)
    await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f'`{command}` failed with return code {proc.returncode}')
