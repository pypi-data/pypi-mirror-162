from typing import Iterator

from .statement import Statement

PREAMBLE = '''
import asyncio
import aiohttp
import api_query.lib as __lib

async def __run_query(__session: aiohttp.ClientSession, __limit: __lib.ConcurrencyLimit) -> None:
    __lib.resolve_imports()
'''

POSTAMBLE = '''

async def __query_async(max_concurrent: int) -> None:
    async with aiohttp.ClientSession() as session:
        await __run_query(session, __lib.ConcurrencyLimit(max_concurrent))

def __query(max_concurrent: int) -> None:
    asyncio.run(__query_async(max_concurrent))

if __name__ == "__main__":
    import argparse
    __parser = argparse.ArgumentParser("Run API query.")
    __parser.add_argument("--max-concurrent", type=int, default=1,
                          help="Max number of concurrent statement executions allowed.")
    __parser.add_argument("--log-level", type=str, default='info',
                          choices=['debug', 'info', 'warning', 'error', 'fatal'],
                          help="Log level.")
    __args, __ = __parser.parse_known_args()

    __lib.set_log_level(__args.log_level)
    __query(__args.max_concurrent)
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
