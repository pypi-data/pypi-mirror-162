from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from io import StringIO
import re
import shlex
import tokenize
from typing import Any, Callable, NamedTuple

from funcparserlib.lexer import Token, LexerError

class Position(NamedTuple):
    line: int
    char: int
    offset: int

@dataclass(frozen=True, slots=True)
class Slice:
    raw: str
    start: Position
    # end is inclusive
    end: Position

    def __add__(self, s: Slice) -> Slice:
        assert self.raw == s.raw, 'Cannot add slices of different strings'
        assert self.end.offset == s.start.offset - 1, 'Cannot add non-contiguous slices'
        return Slice(self.raw, self.start, s.end)

    def __getitem__(self, val: int | slice) -> Slice:
        length = self.end.offset - self.start.offset + 1
        if isinstance(val, int):
            start = end = val if val >= 0 else length + val
        else:
            start = 0 if val.start is None else val.start
            end = length if val.stop is None else val.stop
            if start < 0:
                start += length
            elif start >= length:
                start = length - 1
            if end < 0:
                end += length
            elif end >= length:
                end = length
            end -= 1

        assert 0 <= start <= end <= length, "only non-empty slices are supported"

        if self.start.line == self.end.line:
            return Slice(
                    self.raw,
                    Position(self.start.line, self.start.char + start, self.start.offset + start),
                    Position(self.start.line, self.start.char + end, self.start.offset + end))
        else:
            offset_start = self.start.offset + start
            offset_end = self.start.offset + end

            nl_to_start = self.raw.count('\n', self.start.offset, offset_start)
            if nl_to_start == 0:
                start_pos = self.start.char + start
            else:
                start_pos = offset_start - self.raw.rfind('\n', self.start.offset, offset_start)
            if self.start.line + nl_to_start == self.end.line:
                nl_to_end = nl_to_start
            else:
                nl_to_end = nl_to_start + self.raw.count('\n', offset_start, offset_end)
            if nl_to_end == 0:
                end_pos = self.start.char + end
            else:
                end_pos = offset_end - self.raw.rfind('\n', self.start.offset, offset_end)
            return Slice(
                    self.raw,
                    Position(self.start.line + nl_to_start, start_pos, self.start.offset + start),
                    Position(self.start.line + nl_to_end, end_pos, self.start.offset + end))

    def get(self) -> str:
        return self.raw[self.start.offset : self.end.offset + 1]

    def to_eol(self) -> tuple[Slice | None, Slice | None]:
        index = self.raw.find('\n', self.start.offset, self.end.offset)
        if index == self.start.offset:
            return None, self
        elif self.start.offset < index < self.end.offset:
            pivot = index - self.start.offset
            return self[:pivot], self[pivot:]
        else:
            return self, None

    def consume_eol(self) -> tuple[Slice | None, Slice | None]:
        assert self.raw[self.start.offset] == '\n'
        if self.start == self.end:
            return self, None
        else:
            return self[:1], self[1:]

    @classmethod
    def from_str(cls, raw: str) -> Slice | None:
        length = len(raw)
        if length == 0:
            return None
        lines = raw.count('\n', 0, length - 1) + 1
        if lines == 1:
            end = Position(1, length, length - 1)
        else:
            end = Position(lines, (length - 1) - raw.rindex('\n', 0, length - 1), length - 1)
        return cls(raw, Position(1, 1, 0), end)

TokenMatcher = Callable[[Slice, Slice | None], tuple[Slice, Slice | None]]

def match_to_exception(
    fn: Callable[[StringIO], Iterable[Any]],
    exception: type[Exception],
    exception_handler: Callable[[Position, Exception], None] | None
) -> TokenMatcher:
    def match(prefix: Slice, rest: Slice | None) -> tuple[Slice, Slice | None]:
        stream = StringIO()
        pos = prefix.end
        rest_copy = rest
        while rest is not None:
            line, rest = rest.to_eol()
            if line is not None:
                pos = line.end
                stream.write(line.get())
                stream.seek(0)
                try:
                    for _ in fn(stream):
                        pass
                except exception as e:
                    if exception_handler:
                        exception_handler(pos, e)
                else:
                    break
            if rest is not None:
                eol, rest = rest.consume_eol()
                assert eol is not None
                pos = eol.end
                stream.write(eol.get())
        else:
            raise LexerError(pos[:2], 'Unexpected EOF')

        assert rest_copy is not None
        return rest_copy[:stream.tell()], rest

    return match

def match_to_eol(prefix: Slice, rest: Slice | None) -> tuple[Slice, Slice | None]:
    out = prefix
    while rest is not None:
        line, rest = rest.to_eol()
        if line is None:
            return out, rest
        out += line

        value = line.get()
        i = len(value) - 1
        for i in range(len(value) - 1, -1, -1):
            if value[i] != '\\':
                break
        num_slashes = len(value) - 1 - i

        if num_slashes % 2 == 0:
            return out, rest

        if rest:
            eol, rest = rest.consume_eol()
            assert eol is not None
            out += eol
    else:
        raise LexerError(out.end[:2], 'Unexpected EOF')

def match_simple(prefix: Slice, rest: Slice | None) -> tuple[Slice, Slice | None]:
    return prefix, rest

def check_tokenize_error(pos: Position, e: Exception) -> None:
    if not isinstance(e, tokenize.TokenError) or not e.args[0].startswith('EOF in multi-line'):
        raise LexerError(pos[:2], f'Error reading Python: {e}')

_SPECS = [
    ('LINECOMMENT', r'#|//', match_to_eol),
    ('PYTHON', r'!\s*',
        match_to_exception(lambda s: tokenize.generate_tokens(s.readline), tokenize.TokenError,
                           check_tokenize_error)),
    ('SHELL', r'>\s*', match_to_exception(lambda s: shlex.split(s.read()), ValueError, None)),
    ('HTTP', r'(?:GET|HEAD|POST|PUT|DELETE|PATCH|OPTIONS) ', match_to_eol),
    ('HEADER', r'-\s*[A-Za-z_-]+\s*:', match_to_eol),
    ('ASSIGN', r'[A-Za-z_][A-Za-z0-9_]*\s*=', match_to_eol),
    ('COMMENT', r'/\*(?:[^*]|\*[^/])+\*/', match_to_eol),
    ('SPACE', r'\s+', match_simple),
    ('COLON', r':', match_simple),
    ('ARROW', r'->', match_simple),
    ('LBRACKET', r'{', match_simple),
    ('RBRACKET', r'}', match_simple),
    ('LSQUARE', r'\[', match_simple),
    ('RSQUARE', r'\]', match_simple),
    ('DOT', r'\.', match_simple),
    ('DASH', r'-', match_simple),
    ('COMMA', r',', match_simple),
    ('INTEGER', r'-?(?:0|[1-9][0-9]*)', match_simple),
    ('FLOAT', r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]*)?(?:[eE][+-]?[0-9]+)?', match_simple),
    ('TRUE', r'true', match_simple),
    ('FALSE', r'false', match_simple),
    ('NULL', r'null', match_simple),
    ('STRING', r'"(?:[^"\\]|\\(?:["\\/bfnrt]|u[0-9A-Fa-f]{4}))*"', match_simple),
    ('IDENTIFIER', r'[A-Za-z0-9_-]+', match_simple),
]
SPECS = [(name, re.compile(r), matcher) for name, r, matcher in _SPECS]

def simple_lex(data: str) -> Iterator[Token]:
    if not data:
        raise LexerError((0, 0), 'Empty input')

    rest = Slice.from_str(data)
    while rest is not None:
        for name, prefix_regex, matcher in SPECS:
            m = prefix_regex.match(rest.raw, rest.start.offset)
            if m is not None:
                start = m.start() - rest.start.offset
                end = m.end() - rest.start.offset

                prefix = rest[start:end]
                if prefix.end == rest.end:
                    rest = None
                else:
                    rest = rest[end:]

                out, rest = matcher(prefix, rest)
                yield Token(name, out.get(), out.start[:2], out.end[:2])
                break
        else:
            raise LexerError(rest.start[:2], 'No match found')

def lex(data: str) -> Iterator[Token]:
    for token in simple_lex(data):
        if token.type not in ('LINECOMMENT', 'COMMENT', 'SPACE'):
            yield token

if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rt') as f:
        for token in lex(f.read()):
            print(token)
