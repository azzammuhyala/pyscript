from collections.abc import Iterable
from functools import reduce
from html.parser import HTMLParser
from operator import or_

from .generic import dfrozen, get_sequence

DEFAULT = 0
BACKGROUND = 1 << 0
BOLD = 1 << 1
FAINT = 1 << 2
ITALIC = 1 << 3
UNDERLINE = 1 << 4
BLINK = 1 << 5
RAPIDBLINK = 1 << 6
STRIKETHROUGH = 1 << 7
DOUBLEUNDERLINE = 1 << 8

ANSI_NAMES_MAP = dfrozen({
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

FLAG_NAMES_MAP = dfrozen({
    'DEFAULT': DEFAULT,
    'BACKGROUND': BACKGROUND,
    'BOLD': BOLD,
    'FAINT': FAINT,
    'ITALIC': ITALIC,
    'UNDERLINE': UNDERLINE,
    'BLINK': BLINK,
    'RAPIDBLINK': RAPIDBLINK,
    'STRIKETHROUGH': STRIKETHROUGH,
    'DOUBLEUNDERLINE': DOUBLEUNDERLINE
})

STYLE_CODES_MAP = dfrozen({
    BOLD: '1',
    FAINT: '2',
    ITALIC: '3',
    UNDERLINE: '4',
    BLINK: '5',
    RAPIDBLINK: '6',
    STRIKETHROUGH: '9',
    DOUBLEUNDERLINE: '21'
})

def acolor(*args, style: int = DEFAULT) -> str:
    if not args:
        arg = None
    elif len(args) == 1:
        arg = args[0]
    else:
        arg = args

    styles = [code for flag, code in STYLE_CODES_MAP.items() if style & flag]
    style_string = f'\x1b[{";".join(styles)}m' if styles else ''
    if arg is None:
        return style_string

    offset = 10 if style & BACKGROUND else 0

    if isinstance(arg, str):
        color = arg.strip().lower().replace(' ', '-').replace('_', '-')
        if color in ANSI_NAMES_MAP:
            return f'{style_string}\x1b[{ANSI_NAMES_MAP[color] + offset}m'
        arg = arg.replace(',', ' ').split()

    if isinstance(arg, Iterable):
        color = tuple(map(int, arg))
        if len(color) == 3 and all(0 <= c <= 255 for c in color):
            return f'{style_string}\x1b[{38 + offset};2;{";".join(map(str, color))}m'

    raise TypeError("acolor(): the argument is invalid for ansi color")

SPECIAL_TAGS = dfrozen({
    name: acolor(name) for name in ANSI_NAMES_MAP.keys()
} | {
    'b': acolor(style=BOLD),
    'i': acolor(style=ITALIC),
    'u': acolor(style=UNDERLINE),
    's': acolor(style=STRIKETHROUGH),
    'mark': acolor('yellow', style=BACKGROUND),
    'blink': acolor(style=BLINK)
})

class AnsiParser(HTMLParser):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.result = ''
        self.stack = []

    def _get_last_stack(self) -> str:
        return get_sequence(self.stack, -1, ('', '\x1b[0m'))[1]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'ansi':
            attrs = dict(attrs)
            color = acolor(
                attrs.get('color'),
                style=reduce(or_, (
                    FLAG_NAMES_MAP[style.upper()]
                    for style in
                    attrs.get('style', 'DEFAULT').replace(',', ' ').split()
                ))
            )
        elif tag in SPECIAL_TAGS:
            color = SPECIAL_TAGS[tag]
        else:
            raise ValueError(f"unknown start-tag: {tag}")

        if self._get_last_stack() != color:
            self.result += color
        self.stack.append((tag, color))

    def handle_endtag(self, tag: str) -> None:
        if not (tag == 'ansi' or tag in SPECIAL_TAGS):
            raise ValueError(f"unknown end-tag: {tag}")
        if not self.stack or tag != self.stack[-1][0]:
            raise SyntaxError("unmatch end-tag")

        _, color = self.stack.pop()
        last = self._get_last_stack()

        if color and color != last:
            self.result += '\x1b[0m'
            if self.stack:
                self.result += last

    def handle_data(self, data: str) -> None:
        self.result += data

    def get_output(self) -> str:
        if self.stack:
            raise SyntaxError("unmatch tag got EOF")
        return self.result

def ahtml(string: str) -> str:
    parser = AnsiParser()
    parser.feed(string)
    parser.close()
    return parser.get_output()

__all__ = (
    'ANSI_NAMES_MAP',
    'DEFAULT',
    'BACKGROUND',
    'BOLD',
    'FAINT',
    'ITALIC',
    'UNDERLINE',
    'BLINK',
    'RAPIDBLINK',
    'STRIKETHROUGH',
    'DOUBLEUNDERLINE',
    'acolor',
    'AnsiParser',
    'ahtml'
)