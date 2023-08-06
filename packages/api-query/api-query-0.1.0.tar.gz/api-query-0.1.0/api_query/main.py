import argparse

from .compiler import compile
from .lexer import lex
from .parser import parse

def main() -> None:
    parser = argparse.ArgumentParser(description="Run API query.")
    parser.add_argument("file", type=str,
                        help="Query file.")
    parser.add_argument("--max-concurrent", type=int, default=1,
                        help="Max number of concurrent statement executions allowed.")
    parser.add_argument("--log-level", type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error', 'fatal'],
                        help="Log level.")
    args = parser.parse_args()

    with open(args.file, 'rt') as f:
        source = '\n'.join(compile(parse(lex(f.read()))))

    exec(source, {'__name__': '__main__'})

if __name__ == '__main__':
    main()
