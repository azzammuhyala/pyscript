from collections.abc import Iterable
from io import IOBase, TextIOWrapper
from json import detect_encoding
from re import compile as compile_regex
from types import BuiltinMethodType
from typing import Sequence

sub_newline = compile_regex(r'\r\n|[\r\v]').sub

def normstr(obj) -> str:
    if isinstance(obj, str):
        return sub_newline('\n', obj)

    elif isinstance(obj, (bytes, bytearray)):
        return normstr(obj.decode(detect_encoding(obj), 'surrogatepass'))

    elif isinstance(obj, IOBase):
        if not obj.readable():
            raise TypeError("unreadable IO")
        return normstr(obj.read())

    elif isinstance(obj, Iterable):
        return ''.join(map(normstr, obj))

    elif (
        isinstance(obj, BuiltinMethodType) and
        isinstance(self := getattr(obj, '__self__', None), TextIOWrapper) and
        obj.__name__ == 'readline'
    ):
        if not self.readable():
            raise TypeError("unreadable IO, provides readline function")
        lines = ''
        while line := obj():
            lines += normstr(line)
        return lines

    raise TypeError(f"cannot normalize {type(obj).__name__} to str")

def join(sequence: Sequence[str], conjunction: str = 'and') -> str:
    length = len(sequence)
    if length == 1:
        return sequence[0]
    elif length == 2:
        return f'{sequence[0]} {conjunction} {sequence[1]}'
    return f'{", ".join(sequence[:-1])}, {conjunction} {sequence[-1]}'

def indent(string: str, length: int, indent: str = ' ') -> str:
    prefix = indent * length
    return prefix + normstr(string).replace('\n', '\n' + prefix)