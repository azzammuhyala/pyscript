from collections.abc import Iterator
from io import IOBase
from json import detect_encoding

def normstr(obj):
    if isinstance(obj, str):
        return obj.replace('\r\n', '\n').replace('\r', '\n')

    elif isinstance(obj, (bytes, bytearray)):
        return normstr(obj.decode(detect_encoding(obj), 'surrogatepass'))

    elif isinstance(obj, IOBase):
        if not obj.readable():
            raise TypeError("unreadable IO")
        return normstr(obj.read())

    elif isinstance(obj, Iterator):
        return '\n'.join(map(normstr, obj))

    elif callable(obj):
        lines = []
        while True:
            if not (line := obj()):
                break
            lines.append(normstr(line))
        return '\n'.join(lines)

    raise TypeError('not a string')

def join(sequence, conjunction='and'):
    length = len(sequence)
    if length == 1:
        return sequence[0]
    elif length == 2:
        return f'{sequence[0]} {conjunction} {sequence[1]}'
    return f'{", ".join(sequence[:-1])}, {conjunction} {sequence[-1]}'

def indent(string, length):
    prefix = ' ' * length
    return '\n'.join(prefix + line for line in normstr(string).splitlines())