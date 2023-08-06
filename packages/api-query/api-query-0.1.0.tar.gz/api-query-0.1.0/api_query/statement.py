from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence, NamedTuple

class Statement(ABC):
    __slots__: Sequence[str] = tuple()

    @abstractmethod
    def compile(self, indent: str = '') -> str:
        pass

class Identifier(str):
    __slots__: Sequence[str] = tuple()

    def __repr__(self) -> str:
        return str(self)

class OutputIdentifier(Identifier):
    __slots__: Sequence[str] = tuple()

    def __repr__(self) -> str:
        return f'OutputIdentifier({super(Identifier, self).__repr__()})'

class _Placeholder:
    __slots__: Sequence[str] = tuple()

    def __str__(self) -> str:
        return 'Placeholder'

    def __repr__(self) -> str:
        return 'None'
Placeholder = _Placeholder()

TemplateValue = int | float | bool | str | None | Identifier | _Placeholder

RequestTemplateObject = dict[str, 'RequestTemplate']
RequestTemplateArray = list['RequestTemplate']
RequestTemplate = TemplateValue | RequestTemplateObject | RequestTemplateArray

ResponseTemplateObject = dict[str, 'ResponseTemplate']
ResponseTemplateArray = list['ResponseTemplate']

class ResponseTemplateArrayHandler(NamedTuple):
    template: 'ResponseTemplate'
    handler: list[Statement]

    @classmethod
    def make(cls, args: tuple['ResponseTemplate', list[Statement]]) -> ResponseTemplateArrayHandler:
        return cls(*args)

ResponseTemplate = TemplateValue | OutputIdentifier | ResponseTemplateObject | ResponseTemplateArray | \
                   ResponseTemplateArrayHandler

@dataclass(slots=True)
class PythonStatement(Statement):
    source: str

    @classmethod
    def from_assignment(cls, key: str, value: str) -> PythonStatement:
        if value:
            return cls(source=f"{key} = f'''{value}'''")
        else:
            return cls(source=f"{key} = os.environ.get('{key}', '')")

    def compile(self, indent: str = '') -> str:
        return (
            f'{indent}async with __limit:\n'
            f'{indent}    __lib.LOG.info("Running python: " {repr(self.source.strip())})\n'
            f'{indent}    {self.source.strip()}\n'
        )

@dataclass(slots=True)
class ShellStatement(Statement):
    source: str

    def compile(self, indent: str = '') -> str:
        return (
            f'{indent}async with __limit:\n'
            f'{indent}    __lib.LOG.info("Running shell: " {repr(self.source.strip())})\n'
            f'{indent}    await __lib.run_shell(f{repr(self.source.strip())})\n'
        )

@dataclass(slots=True)
class HTTPStatement(Statement):
    method: str
    url: str
    headers: dict[str, str]
    body: RequestTemplateObject | RequestTemplateArray | str | None
    response: ResponseTemplateObject | ResponseTemplateArray | OutputIdentifier

    def _output_headers(self, indent: str = '') -> str:
        if not self.headers: return '{}'
        return (
             '{\n' +
             ''.join(f'{indent}    {repr(key)}: f{repr(value)}\n' for key, value in self.headers.items()) +
            f'{indent}}}'
        )

    def _output_response_object(
            self, response: ResponseTemplateObject, sfx: str, path: str, indent: str) -> str:
        return (
            f'{indent}assert isinstance(__p{sfx}, dict), f"{path} in response is not an object"\n' +
            ''.join((
                f'{indent}assert {repr(k)} in __p{sfx}, f"{path} in response has no key " + repr({repr(k)})\n'
                f'{indent}__p{id(r)} = __p{sfx}[{repr(k)}]\n' +
                self._output_response_general(r, str(id(r)), f'{path}.{k}', indent) +
                f'{indent}del __p{id(r)}\n'
            ) for k, r in response.items())
        )

    def _output_response_array_element(
            self, sfx: str, path: str, key: int, value: ResponseTemplate, indent: str) -> str:
        r = self._output_response_general(value, str(id(value)), f'{path}[{key}]', indent)
        if not r:
            return ''
        return (
            f'{indent}assert len(__p{sfx}) > {key}, f"{path} in response has fewer than {key + 1} elements"\n'
            f'{indent}__p{id(value)} = __p{sfx}[{repr(key)}]\n'
            f'{r}'
            f'{indent}del __p{id(value)}\n'
        )

    def _output_response_array(
            self, response: ResponseTemplateArray, sfx: str, path: str, indent: str) -> str:
        return (
            f'{indent}assert isinstance(__p{sfx}, list), f"{path} in response is not an array"\n' +
            ''.join(self._output_response_array_element(sfx, path, i, r, indent) for i, r in enumerate(response))
        )

    def _output_response_array_handler(
            self, response: ResponseTemplateArrayHandler, sfx: str, path: str, indent: str) -> str:
        return (
            f'{indent}assert isinstance(__p{sfx}, list), f"{path} in response is not an array"\n\n'
            f'{indent}async def __f{sfx}(__p{sfx}_e):\n' +
            f'{indent}    __lib.resolve_imports()\n' +
            self._output_response_general(response.template, f'{sfx}_e', f'{path}[]', indent + '    ') +
            ''.join(f'{stmt.compile(indent=indent + "    ")}\n' for stmt in response.handler) +
            f'\n'
            f'{indent}await asyncio.gather(*{{__f{sfx}(__p{sfx}_e) for __p{sfx}_e in __p{sfx}}})\n'
            f'{indent}del __f{sfx}\n'
        )


    def _output_response_general(
            self, response: ResponseTemplate, sfx: str, path: str, indent: str = '') -> str:
        if isinstance(response, _Placeholder):
            return ''
        if isinstance(response, OutputIdentifier):
            return f'{indent}{response} = __p{sfx}\n'
        elif isinstance(response, str | int | float | bool | None | Identifier):
            return (
                f'{indent}assert __p{sfx} == {repr(response)}, "{path} in response not equal to " + '
                        f'repr({repr(response)})\n'
            )
        elif isinstance(response, dict):
            return self._output_response_object(response, sfx, path, indent)
        elif isinstance(response, list):
            return self._output_response_array(response, sfx, path, indent)
        else:
            return self._output_response_array_handler(response, sfx, path, indent)

    def _output_response(self, sfx: str, indent: str = '') -> str:
        return self._output_response_general(self.response, sfx, 'RESPONSE', indent)

    def compile(self, indent: str = '') -> str:
        sfx = f'{id(self)}'
        body_value = repr(self.body) if not isinstance(self.body, str) else f'f"{self.body}"'
        data_arg = (
            f'data=__body{sfx}'
            if isinstance(self.body, str) else
            f'json=__body{sfx}'
            if self.body is not None else
            ''
        )
        response_type = 'text' if isinstance(self.response, OutputIdentifier) else 'json'
        return (
                f'{indent}__headers{sfx} = {self._output_headers(indent)}\n'
                f'{indent}__body{sfx} = {body_value}\n'
                f'{indent}__url{sfx} = f{repr(self.url)}\n'
                f'{indent}async with __limit:\n'
                f'{indent}    __lib.LOG.info(f"Running {self.method} request to: {{__url{sfx}}}")\n'
                f'{indent}    __lib.LOG.debug(f"Headers: {{__headers{sfx}}}, body: {{__body{sfx}}}")\n'
                f'{indent}    async with __session.{self.method.lower()}(__url{sfx}, '
                                      f'headers=__headers{sfx}, {data_arg}) as __response{sfx}:\n'
                f'{indent}        __p{sfx} = await __response{sfx}.{response_type}()\n'
                f'{indent}__lib.LOG.debug(f"Response for {{__url{sfx}}}: {{__p{sfx}}}")\n'
                f'{self._output_response(sfx, indent)}'
                f'{indent}del __headers{sfx}, __body{sfx}, __url{sfx}, __p{sfx}, __response{sfx}\n'
        )
