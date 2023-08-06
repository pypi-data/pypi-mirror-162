from typing import Iterator

from .statement import Statement

PREAMBLE = '''
import asyncio
import aiohttp
import api_query.lib as __lib

async def __run_query(__session: aiohttp.ClientSession,
                      __stmt_limit: __lib.ConcurrencyLimit,
                      __http_limit: __lib.RateLimit,
                      __http_retry: __lib.RetryConfig) -> None:
    __lib.resolve_imports()
'''

POSTAMBLE = '''

async def __query_async(max_concurrent: int, http_rate_limit: int, http_retry: __lib.RetryConfig) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            await __run_query(session,
                              __lib.ConcurrencyLimit(max_concurrent),
                              __lib.RateLimit(http_rate_limit),
                              http_retry)
        except Exception as e:
             __lib.LOG.error(str(e))

def __query(max_concurrent: int, http_rate_limit: int, http_retry: __lib.RetryConfig) -> None:
    asyncio.run(__query_async(max_concurrent, http_rate_limit, http_retry))

if __name__ == "__main__":
    import argparse
    __parser = argparse.ArgumentParser("Run API query.")
    __parser.add_argument("--max-concurrent", type=int, default=1,
                          help="Max number of concurrent statement executions allowed.")
    __parser.add_argument("--log-level", type=str, default='info',
                          choices=['debug', 'info', 'warning', 'error', 'fatal'],
                          help="Log level.")
    __parser.add_argument("--http-rate-limit", type=int, default=1,
                          help="Max number of HTTP queries per second.")
    __parser.add_argument("--http-retry-count", type=int, default=1,
                          help="Max number of times to retry HTTP queries.")
    __parser.add_argument("--http-base-delay", type=float, default=1.0,
                          help="Base delay between HTTP query retries.")
    __parser.add_argument("--http-max-delay", type=float, default=10.0,
                          help="Max delay between HTTP query retries.")
    __args, __ = __parser.parse_known_args()

    __lib.set_log_level(__args.log_level)
    __query(__args.max_concurrent, __args.http_rate_limit,
            __lib.RetryConfig(__args.http_retry_count, __args.http_base_delay, __args.http_max_delay))
'''

def compile(statements: Iterator[Statement]) -> Iterator[str]:
    yield PREAMBLE
    for statement in statements:
        yield statement.compile(indent='    ')
    yield POSTAMBLE

if __name__ == '__main__':
    import sys
    from .lexer import lex
    from .parser import parse
    with open(sys.argv[1], 'rt') as f:
        for x in compile(parse(lex(f.read()))):
            print(x)
