from .bases import Pys
from .utils.decorators import TYPECHECK_STACK, immutable
from .utils.generic import setimuattr

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .position import PysPosition

DOUBLE = 2**8
TRIPLE = 2**9
WITH_EQUAL = 2**10
SPECIAL = 2**11

TOKENS = MappingProxyType({
    'NULL': ord('\0'),
    'KEYWORD': 0x01,
    'IDENTIFIER': 0x02,
    'NUMBER': 0x03,
    'STRING': 0x04,
    'NOT_IN': 0x05,
    'IS_NOT': 0x06,
    'NEWLINE': ord('\n'),
    'EXCLAMATION': ord('!'),
    'COMMENT': ord('#'),
    'PERCENT': ord('%'),
    'AMPERSAND': ord('&'),
    'RIGHT_PARENTHESIS': ord(')'),
    'LEFT_PARENTHESIS': ord('('),
    'STAR': ord('*'),
    'PLUS': ord('+'),
    'COMMA': ord(','),
    'MINUS': ord('-'),
    'DOT': ord('.'),
    'SLASH': ord('/'),
    'COLON': ord(':'),
    'SEMICOLON': ord(';'),
    'LESS_THAN': ord('<'),
    'EQUAL': ord('='),
    'GREATER_THAN': ord('>'),
    'QUESTION': ord('?'),
    'AT': ord('@'),
    'LEFT_SQUARE': ord('['),
    'RIGHT_SQUARE': ord(']'),
    'CIRCUMFLEX': ord('^'),
    'LEFT_CURLY': ord('{'),
    'PIPE': ord('|'),
    'RIGHT_CURLY': ord('}'),
    'TILDE': ord('~'),
    'DOUBLE_AMPERSAND': ord('&') + DOUBLE,
    'DOUBLE_STAR': ord('*') + DOUBLE,
    'DOUBLE_PLUS': ord('+') + DOUBLE,
    'DOUBLE_MINUS': ord('-') + DOUBLE,
    'DOUBLE_SLASH': ord('/') + DOUBLE,
    'DOUBLE_LESS_THAN': ord('<') + DOUBLE,
    'DOUBLE_EQUAL': ord('=') + DOUBLE,
    'DOUBLE_GREATER_THAN': ord('>') + DOUBLE,
    'DOUBLE_QUESTION': ord('?') + DOUBLE,
    'DOUBLE_PIPE': ord('|') + DOUBLE,
    'TRIPLE_DOT': ord('.') + TRIPLE,
    'EQUAL_EXCLAMATION': ord('!') + WITH_EQUAL,
    'EQUAL_PERCENT': ord('%') + WITH_EQUAL,
    'EQUAL_AMPERSAND': ord('&') + WITH_EQUAL,
    'EQUAL_STAR': ord('*') + WITH_EQUAL,
    'EQUAL_PLUS': ord('+') + WITH_EQUAL,
    'EQUAL_MINUS': ord('-') + WITH_EQUAL,
    'EQUAL_SLASH': ord('/') + WITH_EQUAL,
    'EQUAL_COLON': ord(':') + WITH_EQUAL,
    'EQUAL_LESS_THAN': ord('<') + WITH_EQUAL,
    'EQUAL_GREATER_THAN': ord('>') + WITH_EQUAL,
    'EQUAL_AT': ord('@') + WITH_EQUAL,
    'EQUAL_CIRCUMFLEX': ord('^') + WITH_EQUAL,
    'EQUAL_PIPE': ord('|') + WITH_EQUAL,
    'EQUAL_TILDE': ord('~') + WITH_EQUAL,
    'EQUAL_DOUBLE_STAR': ord('*') + DOUBLE + WITH_EQUAL,
    'EQUAL_DOUBLE_SLASH': ord('/') + DOUBLE + WITH_EQUAL,
    'EQUAL_DOUBLE_LESS_THAN': ord('<') + DOUBLE + WITH_EQUAL,
    'EQUAL_DOUBLE_GREATER_THAN': ord('>') + DOUBLE + WITH_EQUAL,
    'NONE': SPECIAL,
    'MINUS_GREATER_THAN': ord('-') + SPECIAL,
    'EQUAL_ARROW': ord('>') + SPECIAL,
    'EXCLAMATION_GREATER_THAN': ord('!') + SPECIAL,
    'EXCLAMATION_TILDE': ord('~') + SPECIAL,
    'LESS_THAN_GREATER_THAN': ord('<') + SPECIAL
})

@immutable
class PysToken(Pys):

    __slots__ = ('type', 'position', 'value')

    # cannot use @pyscript.core.utils.decorator.typecheck because the 'PysPosition' annotation is unknown at runtime
    # so checking arguments is doing manually.
    def __init__(self, type: int, position: 'PysPosition', value: Optional[Any] = None) -> None:
        if TYPECHECK_STACK > 0:
            if not isinstance(type, int):
                raise TypeError('type must be integer')
            # circular import solved
            from .position import PysPosition
            if not isinstance(position, PysPosition):
                raise TypeError('position must be pyscript.core.position.PysPosition')

        setimuattr(self, 'type', type)
        setimuattr(self, 'position', position)
        setimuattr(self, 'value', value)

    def __repr__(self) -> str:
        # circular import solved
        from .mapping import REVERSE_TOKENS
        value = '' if self.value is None else f', {self.value!r}'
        return f'Token({REVERSE_TOKENS.get(self.type, "<UNKNOWN>")}{value})'

    def match(self, type: int, *values: Any) -> bool:
        return self.type == type and self.value in values