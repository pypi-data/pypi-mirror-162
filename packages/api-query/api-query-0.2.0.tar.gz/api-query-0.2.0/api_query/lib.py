"""
    Helper functions used by the generated script.
"""

import asyncio
import time
import importlib
import logging
import sys
from types import TracebackType
from typing import NamedTuple


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


class RateLimit:
    def __init__(self, max_qps: int) -> None:
        self.token_interval = 1.0 / max_qps
        self.last_token_time = 0
        self.max_tokens = max_qps
        self.tokens = max_qps
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.BoundedSemaphore(self.tokens)

    async def _update_tokens(self) -> None:
        while True:
            async with self.lock:
                now = time.time()
                if self.tokens < self.max_tokens and now - self.last_token_time > self.token_interval:
                    new_tokens = min(self.max_tokens - self.tokens,
                                     int((now - self.last_token_time) / self.token_interval))
                    self.tokens += new_tokens
                    if self.tokens == self.max_tokens:
                        self.last_token_time = now
                    else:
                        self.last_token_time += new_tokens * self.token_interval
                    for _ in range(new_tokens):
                        self.semaphore.release()
            await asyncio.sleep(self.token_interval)

    async def get_token(self) -> None:
        update_task = asyncio.create_task(self._update_tokens())
        acquire_task = asyncio.create_task(self.semaphore.acquire())
        finished, unfinished = await asyncio.wait({update_task, acquire_task},
                                                  return_when=asyncio.FIRST_COMPLETED)
        for task in finished:
            task.result()
        assert acquire_task in finished
        for task in unfinished:
            task.cancel()
        async with self.lock:
            self.tokens -= 1


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


class RetryConfig(NamedTuple):
    retry_count: int
    base_delay: float
    max_delay: float
