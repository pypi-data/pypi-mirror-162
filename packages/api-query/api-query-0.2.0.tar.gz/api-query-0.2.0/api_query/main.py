import argparse

from . import compile

def main() -> None:
    parser = argparse.ArgumentParser(description="Run API query.")
    parser.add_argument("file", type=str,
                        help="Query file.")
    parser.add_argument("--compile-only", action='store_true',
                        help="Only compile the query and print resulting Python code to stdout.")
    parser.add_argument("--max-concurrent", type=int, default=1,
                        help="Max number of concurrent statement executions allowed.")
    parser.add_argument("--http-rate-limit", type=int, default=1,
                        help="Max number of HTTP queries per second.")
    parser.add_argument("--http-retry-count", type=int, default=1,
                        help="Max number of times to retry HTTP queries.")
    parser.add_argument("--http-base-delay", type=float, default=1.0,
                        help="Base delay between HTTP query retries.")
    parser.add_argument("--http-max-delay", type=float, default=10.0,
                        help="Max delay between HTTP query retries.")
    parser.add_argument("--log-level", type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error', 'fatal'],
                        help="Log level.")
    args = parser.parse_args()

    with open(args.file, 'rt') as f:
        source = compile(f.read())

    if args.compile_only:
        print(source)
    else:
        exec(source, {'__name__': '__main__'})

if __name__ == '__main__':
    main()
