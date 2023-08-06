from .lexer import lex as _lex
from .parser import parse as _parse
from .compiler import compile as _compile

def compile(query: str) -> str:
    return '\n'.join(_compile(_parse(_lex(query))))
