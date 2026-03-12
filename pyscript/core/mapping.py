from .constants import TOKENS
from .utils.ansi import BOLD, acolor

from operator import (
    not_, is_not, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, floordiv, pow, matmul, mod, and_, or_, xor, lshift,
    rshift, iadd, isub, imul, itruediv, ifloordiv, ipow, imatmul, imod, iand, ior, ixor, ilshift, irshift, pos, neg, inv
)
from types import MappingProxyType

contains = lambda a, b: a in b
not_contains = lambda a, b : a not in b
and_op = lambda a, b : a and b
or_op = lambda a, b : a or b

EMPTY_MAP = {}

GET_BINARY_FUNCTIONS_MAP = {
    TOKENS['NOT_IN']: not_contains,
    TOKENS['IS_NOT']: is_not,
    TOKENS['PERCENT']: mod,
    TOKENS['AMPERSAND']: and_,
    TOKENS['STAR']: mul,
    TOKENS['PLUS']: add,
    TOKENS['MINUS']: sub,
    TOKENS['SLASH']: truediv,
    TOKENS['LESS_THAN']: lt,
    TOKENS['GREATER_THAN']: gt,
    TOKENS['AT']: matmul,
    TOKENS['CIRCUMFLEX']: xor,
    TOKENS['PIPE']: or_,
    # TOKENS['DOUBLE_AMPERSAND']: and_op,
    TOKENS['DOUBLE_STAR']: pow,
    TOKENS['DOUBLE_SLASH']: floordiv,
    TOKENS['DOUBLE_LESS_THAN']: lshift,
    TOKENS['DOUBLE_EQUAL']: eq,
    TOKENS['DOUBLE_GREATER_THAN']: rshift,
    # TOKENS['DOUBLE_PIPE']: or_op,
    TOKENS['EQUAL_EXCLAMATION']: ne,
    TOKENS['EQUAL_PERCENT']: imod,
    TOKENS['EQUAL_AMPERSAND']: iand,
    TOKENS['EQUAL_STAR']: imul,
    TOKENS['EQUAL_PLUS']: iadd,
    TOKENS['EQUAL_MINUS']: isub,
    TOKENS['EQUAL_SLASH']: itruediv,
    TOKENS['EQUAL_LESS_THAN']: le,
    TOKENS['EQUAL_GREATER_THAN']: ge,
    TOKENS['EQUAL_AT']: imatmul,
    TOKENS['EQUAL_CIRCUMFLEX']: ixor,
    TOKENS['EQUAL_PIPE']: ior,
    TOKENS['EQUAL_DOUBLE_STAR']: ipow,
    TOKENS['EQUAL_DOUBLE_SLASH']: ifloordiv,
    TOKENS['EQUAL_DOUBLE_LESS_THAN']: ilshift,
    TOKENS['EQUAL_DOUBLE_GREATER_THAN']: irshift,
    TOKENS['MINUS_GREATER_THAN']: contains,
    TOKENS['EXCLAMATION_GREATER_THAN']: not_contains
}.__getitem__

GET_UNARY_FUNCTIONS_MAP = {
    # TOKENS['EXCLAMATION']: not_,
    TOKENS['PLUS']: pos,
    TOKENS['MINUS']: neg,
    TOKENS['TILDE']: inv
}.__getitem__

GET_ACOLORS = {
    'reset': acolor('reset'),
    'magenta': acolor('magenta'),
    'bold-magenta': acolor('magenta', style=BOLD),
    'bold-red': acolor('red', style=BOLD)
}.__getitem__

REVERSE_TOKENS = MappingProxyType({type: name for name, type in TOKENS.items()})

BRACKETS_MAP = MappingProxyType({
    TOKENS['LEFT_PARENTHESIS']: TOKENS['RIGHT_PARENTHESIS'],
    TOKENS['LEFT_SQUARE']: TOKENS['RIGHT_SQUARE'],
    TOKENS['LEFT_CURLY']: TOKENS['RIGHT_CURLY']
})

SYMBOLS_TOKEN_MAP = MappingProxyType({
    TOKENS['NOT_IN']: 'not in',
    TOKENS['IS_NOT']: 'is not',
    TOKENS['NULL']: '\0',
    TOKENS['NEWLINE']: '\n',
    TOKENS['EXCLAMATION']: '!',
    TOKENS['COMMENT']: '#',
    TOKENS['PERCENT']: '%',
    TOKENS['AMPERSAND']: '&',
    TOKENS['RIGHT_PARENTHESIS']: ')',
    TOKENS['LEFT_PARENTHESIS']: '(',
    TOKENS['STAR']: '*',
    TOKENS['PLUS']: '+',
    TOKENS['COMMA']: ',',
    TOKENS['MINUS']: '-',
    TOKENS['DOT']: '.',
    TOKENS['SLASH']: '/',
    TOKENS['COLON']: ':',
    TOKENS['SEMICOLON']: ';',
    TOKENS['LESS_THAN']: '<',
    TOKENS['EQUAL']: '=',
    TOKENS['GREATER_THAN']: '>',
    TOKENS['QUESTION']: '?',
    TOKENS['AT']: '@',
    TOKENS['LEFT_SQUARE']: '[',
    TOKENS['RIGHT_SQUARE']: ']',
    TOKENS['CIRCUMFLEX']: '^',
    TOKENS['LEFT_CURLY']: '{',
    TOKENS['PIPE']: '|',
    TOKENS['RIGHT_CURLY']: '}',
    TOKENS['TILDE']: '~',
    TOKENS['DOUBLE_AMPERSAND']: '&&',
    TOKENS['DOUBLE_STAR']: '**',
    TOKENS['DOUBLE_PLUS']: '++',
    TOKENS['DOUBLE_MINUS']: '--',
    TOKENS['DOUBLE_SLASH']: '//',
    TOKENS['DOUBLE_LESS_THAN']: '<<',
    TOKENS['DOUBLE_EQUAL']: '==',
    TOKENS['DOUBLE_GREATER_THAN']: '>>',
    TOKENS['DOUBLE_QUESTION']: '??',
    TOKENS['DOUBLE_PIPE']: '||',
    TOKENS['TRIPLE_DOT']: '...',
    TOKENS['EQUAL_EXCLAMATION']: '!=',
    TOKENS['EQUAL_PERCENT']: '%=',
    TOKENS['EQUAL_AMPERSAND']: '&=',
    TOKENS['EQUAL_STAR']: '*=',
    TOKENS['EQUAL_PLUS']: '+=',
    TOKENS['EQUAL_MINUS']: '-=',
    TOKENS['EQUAL_SLASH']: '/=',
    TOKENS['EQUAL_COLON']: ':=',
    TOKENS['EQUAL_LESS_THAN']: '<=',
    TOKENS['EQUAL_GREATER_THAN']: '>=',
    TOKENS['EQUAL_AT']: '@=',
    TOKENS['EQUAL_CIRCUMFLEX']: '^=',
    TOKENS['EQUAL_PIPE']: '|=',
    TOKENS['EQUAL_TILDE']: '~=',
    TOKENS['EQUAL_DOUBLE_STAR']: '**=',
    TOKENS['EQUAL_DOUBLE_SLASH']: '//=',
    TOKENS['EQUAL_DOUBLE_LESS_THAN']: '<<=',
    TOKENS['EQUAL_DOUBLE_GREATER_THAN']: '>>=',
    TOKENS['MINUS_GREATER_THAN']: '->',
    TOKENS['EQUAL_ARROW']: '=>',
    TOKENS['EXCLAMATION_GREATER_THAN']: '!>',
    TOKENS['EXCLAMATION_TILDE']: '~!'
})