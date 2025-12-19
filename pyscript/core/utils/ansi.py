from collections.abc import Iterable
from types import MappingProxyType

ANSI_NAMES_MAP = MappingProxyType({
    'reset': 0,
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'gray': 90,
    'bright-black': 90,
    'bright-red': 91,
    'bright-green': 92,
    'bright-yellow': 93,
    'bright-blue': 94,
    'bright-magenta': 95,
    'bright-cyan': 96,
    'bright-white': 97
})

DEFAULT = 0
BACKGROUND = 1 << 0
BOLD = 1 << 1
ITALIC = 1 << 2
UNDER = 1 << 3
STRIKET = 1 << 4

def acolor(*args, style=DEFAULT):
    if not args:
        raise TypeError("acolor(): need at least 1 argument")
    elif len(args) == 1:
        arg = args[0]
    else:
        arg = args

    styles = ''

    if style & BOLD:
        styles += '1'
    if style & ITALIC:
        styles += '3'
    if style & UNDER:
        styles += '4'
    if style & STRIKET:
        styles += '9'

    offset = 10 if style & BACKGROUND else 0
    style = f'\x1b[{";".join(styles)}m' if styles else ''

    if isinstance(arg, str):
        if (color := arg.strip().lower().replace(' ', '-').replace('_', '-')) in ANSI_NAMES_MAP:
            return f'{style}\x1b[{ANSI_NAMES_MAP[color] + offset}m'
        arg = arg.split()

    if isinstance(arg, Iterable):
        color = tuple(map(int, arg))
        if len(color) == 3 and all(0 <= c <= 255 for c in color):
            return f'{style}\x1b[{38 + offset};2;{";".join(map(str, color))}m'

    raise TypeError("acolor(): the argument is invalid for ansi color")