import re
from typing import Any, Iterator, TypeVar

from funcparserlib.lexer import Token
from funcparserlib.parser import many, tok, finished, forward_decl, maybe, Parser

from .statement import (Statement, PythonStatement, ShellStatement, HTTPStatement, Identifier,
                        RequestTemplate, RequestTemplateArray, RequestTemplateObject, Placeholder,
                        OutputIdentifier, ResponseTemplate, ResponseTemplateObject, ResponseTemplateArray,
                        ResponseTemplateArrayHandler)

WHITESPACE = re.compile(r'\s+')

T = TypeVar('T')

def make_none(_: Any) -> None:
    return None

def flatten_many(args: tuple[list[T], list[list[T]]]) -> list[T]:
    return args[0] + sum(args[1], [])

def as_list(value: T) -> list[T]:
    return [value]

def process_assign(assign: str) -> PythonStatement:
    name, value = assign.split('=', 1)
    return PythonStatement.from_assignment(name.strip(), value.strip())

def process_headers(headers: list[str]) -> dict[str, str]:
    rv: dict[str, str] = {}
    for header in headers:
        # - Key: Value
        header = header.split('-', 1)[1].strip()
        key, value = (x.strip() for x in header.split(':', 1))
        rv[key] = value
    return rv

def process_bool(value: str) -> bool:
    return value == 'true'

JSONPath = list[str | int]

def process_json_path_obj(args: tuple[JSONPath, JSONPath]) -> JSONPath:
    return args[0] + args[1]

def process_json_path_array(args: tuple[JSONPath, int, JSONPath]) -> JSONPath:
    return args[0] + [args[1]] + args[2]

def process_jsonlike_object(fields: list[tuple[JSONPath, Any]]) -> Any:
    rv: Any = {}
    for key, value in fields:
        pos = rv
        for cur, nxt in zip(key[:-1], key[1:]):
            if isinstance(cur, int) and cur >= len(pos):
                pos += [Placeholder] * (cur - len(pos) + 1)
            if isinstance(cur, int) or cur not in pos:
                pos[cur] = {} if isinstance(nxt, str) else []
            pos = pos[cur]
        last = key[-1]
        if isinstance(last, int) and last >= len(pos):
            pos += [Placeholder] * (last - len(pos) + 1)
        pos[last] = value
    return rv

def make_http_statement(
        args: tuple[str, dict[str, str], RequestTemplateObject | RequestTemplateArray | str | None,
                    ResponseTemplateObject | ResponseTemplateArray | OutputIdentifier]) -> HTTPStatement:
    method, url = (p.strip() for p in WHITESPACE.split(args[0], 1))
    return HTTPStatement(method, url, *args[1:])

def parse(tokens: Iterator[Token]) -> Iterator[Statement]:
    statement: Parser[Token, Statement] = forward_decl()

    assign_statement = tok('ASSIGN') >> process_assign
    python_statement = tok('PYTHON') >> PythonStatement
    shell_statement = tok('SHELL') >> ShellStatement

    headers = many(tok('HEADER')) >> process_headers

    path_id = tok('IDENTIFIER') >> as_list
    array_unit_path = -tok('LSQUARE') + tok('INTEGER') + -tok('RSQUARE') >> int >> as_list
    array_path = path_id + many(array_unit_path) >> flatten_many
    json_path = array_path + many(-tok('DOT') + array_path) >> flatten_many

    value_number = tok('INTEGER') >> int | tok('FLOAT') >> float
    value_str = tok('STRING') >> str
    value_bool = (tok('TRUE') | tok('FALSE')) >> process_bool
    value_null = tok('NULL') >> make_none
    value_id = tok('IDENTIFIER') >> Identifier
    value = value_number | value_str | value_bool | value_null | value_id

    req_value: Parser[Token, RequestTemplate] = forward_decl()
    req_value_object_field = json_path + -tok('COLON') + req_value >> as_list
    req_value_object: Parser[Token, RequestTemplateObject] = \
            -tok('LBRACKET') + \
            req_value_object_field + many(-tok('COMMA') + req_value_object_field) + \
            -tok('RBRACKET') >> flatten_many >> process_jsonlike_object
    req_value_array: Parser[Token, RequestTemplateArray] = \
            -tok('LSQUARE') + \
            (req_value >> as_list) + many(-tok('COMMA') + req_value) + \
            -tok('RSQUARE') >> flatten_many # type: ignore
    req_value.define(req_value_object | req_value_array | value) # type: ignore

    http_body = req_value_object | req_value_array | (tok('STRING') >> eval)

    resp_value: Parser[Token, ResponseTemplate] = forward_decl()
    resp_value_object_check = json_path + -tok('COLON') + resp_value
    resp_value_object_assign = json_path + -tok('ARROW') + (tok('IDENTIFIER') >> OutputIdentifier)
    resp_value_object_field = (resp_value_object_check | resp_value_object_assign) >> as_list
    resp_value_object: Parser[Token, ResponseTemplateObject] = \
            -tok('LBRACKET') + \
            resp_value_object_field + many(-tok('COMMA') + resp_value_object_field) + \
            -tok('RBRACKET') >> flatten_many >> process_jsonlike_object
    resp_value_handler = \
            -tok('LSQUARE') + \
            resp_value + many(statement) + \
            -tok('RSQUARE') >> ResponseTemplateArrayHandler.make
    resp_value_array: Parser[Token, ResponseTemplateArray] = \
            -tok('LSQUARE') + \
            resp_value + many(-tok('COMMA') + resp_value) + \
            -tok('RSQUARE') >> flatten_many # type: ignore
    resp_value.define(resp_value_object | resp_value_handler | resp_value_array | value) # type: ignore

    response = resp_value_object | resp_value_array | \
            (-tok('ARROW') + tok('IDENTIFIER') >> OutputIdentifier)

    http_block: Parser[Token, HTTPStatement] = \
            tok('HTTP') + headers + maybe(-tok('DASH') + http_body) + response \
            >> make_http_statement # type: ignore

    statement.define(assign_statement | python_statement | shell_statement | http_block) # type: ignore

    document = many(statement) + finished

    return iter(document.parse(list(tokens))[0])

if __name__ == '__main__':
    import sys
    from .lexer import lex
    with open(sys.argv[1], 'rt') as f:
        for x in parse(lex(f.read())):
            print(x)
