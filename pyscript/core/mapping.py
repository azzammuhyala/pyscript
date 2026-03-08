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
    TOKENS['NOT-IN']: not_contains,
    TOKENS['IS-NOT']: is_not,
    TOKENS['PERCENT']: mod,
    TOKENS['AMPERSAND']: and_,
    TOKENS['STAR']: mul,
    TOKENS['PLUS']: add,
    TOKENS['MINUS']: sub,
    TOKENS['SLASH']: truediv,
    TOKENS['LESS-THAN']: lt,
    TOKENS['GREATER-THAN']: gt,
    TOKENS['AT']: matmul,
    TOKENS['CIRCUMFLEX']: xor,
    TOKENS['PIPE']: or_,
    # TOKENS['DOUBLE-AMPERSAND']: and_op,
    TOKENS['DOUBLE-STAR']: pow,
    TOKENS['DOUBLE-SLASH']: floordiv,
    TOKENS['DOUBLE-LESS-THAN']: lshift,
    TOKENS['DOUBLE-EQUAL']: eq,
    TOKENS['DOUBLE-GREATER-THAN']: rshift,
    # TOKENS['DOUBLE-PIPE']: or_op,
    TOKENS['EQUAL-EXCLAMATION']: ne,
    TOKENS['EQUAL-PERCENT']: imod,
    TOKENS['EQUAL-AMPERSAND']: iand,
    TOKENS['EQUAL-STAR']: imul,
    TOKENS['EQUAL-PLUS']: iadd,
    TOKENS['EQUAL-MINUS']: isub,
    TOKENS['EQUAL-SLASH']: itruediv,
    TOKENS['EQUAL-LESS-THAN']: le,
    TOKENS['EQUAL-GREATER-THAN']: ge,
    TOKENS['EQUAL-AT']: imatmul,
    TOKENS['EQUAL-CIRCUMFLEX']: ixor,
    TOKENS['EQUAL-PIPE']: ior,
    TOKENS['EQUAL-DOUBLE-STAR']: ipow,
    TOKENS['EQUAL-DOUBLE-SLASH']: ifloordiv,
    TOKENS['EQUAL-DOUBLE-LESS-THAN']: ilshift,
    TOKENS['EQUAL-DOUBLE-GREATER-THAN']: irshift,
    TOKENS['MINUS-GREATER-THAN']: contains,
    TOKENS['EXCLAMATION-GREATER-THAN']: not_contains
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
    TOKENS['LEFT-PARENTHESIS']: TOKENS['RIGHT-PARENTHESIS'],
    TOKENS['LEFT-SQUARE']: TOKENS['RIGHT-SQUARE'],
    TOKENS['LEFT-CURLY']: TOKENS['RIGHT-CURLY']
})

SYMBOLS_TOKEN_MAP = MappingProxyType({
    TOKENS['NOT-IN']: 'not in',
    TOKENS['IS-NOT']: 'is not',
    TOKENS['NULL']: '\0',
    TOKENS['NEWLINE']: '\n',
    TOKENS['EXCLAMATION']: '!',
    TOKENS['COMMENT']: '#',
    TOKENS['PERCENT']: '%',
    TOKENS['AMPERSAND']: '&',
    TOKENS['RIGHT-PARENTHESIS']: ')',
    TOKENS['LEFT-PARENTHESIS']: '(',
    TOKENS['STAR']: '*',
    TOKENS['PLUS']: '+',
    TOKENS['COMMA']: ',',
    TOKENS['MINUS']: '-',
    TOKENS['DOT']: '.',
    TOKENS['SLASH']: '/',
    TOKENS['COLON']: ':',
    TOKENS['SEMICOLON']: ';',
    TOKENS['LESS-THAN']: '<',
    TOKENS['EQUAL']: '=',
    TOKENS['GREATER-THAN']: '>',
    TOKENS['QUESTION']: '?',
    TOKENS['AT']: '@',
    TOKENS['LEFT-SQUARE']: '[',
    TOKENS['RIGHT-SQUARE']: ']',
    TOKENS['CIRCUMFLEX']: '^',
    TOKENS['LEFT-CURLY']: '{',
    TOKENS['PIPE']: '|',
    TOKENS['RIGHT-CURLY']: '}',
    TOKENS['TILDE']: '~',
    TOKENS['DOUBLE-AMPERSAND']: '&&',
    TOKENS['DOUBLE-STAR']: '**',
    TOKENS['DOUBLE-PLUS']: '++',
    TOKENS['DOUBLE-MINUS']: '--',
    TOKENS['DOUBLE-SLASH']: '//',
    TOKENS['DOUBLE-LESS-THAN']: '<<',
    TOKENS['DOUBLE-EQUAL']: '==',
    TOKENS['DOUBLE-GREATER-THAN']: '>>',
    TOKENS['DOUBLE-QUESTION']: '??',
    TOKENS['DOUBLE-PIPE']: '||',
    TOKENS['TRIPLE-DOT']: '...',
    TOKENS['EQUAL-EXCLAMATION']: '!=',
    TOKENS['EQUAL-PERCENT']: '%=',
    TOKENS['EQUAL-AMPERSAND']: '&=',
    TOKENS['EQUAL-STAR']: '*=',
    TOKENS['EQUAL-PLUS']: '+=',
    TOKENS['EQUAL-MINUS']: '-=',
    TOKENS['EQUAL-SLASH']: '/=',
    TOKENS['EQUAL-COLON']: ':=',
    TOKENS['EQUAL-LESS-THAN']: '<=',
    TOKENS['EQUAL-GREATER-THAN']: '>=',
    TOKENS['EQUAL-AT']: '@=',
    TOKENS['EQUAL-CIRCUMFLEX']: '^=',
    TOKENS['EQUAL-PIPE']: '|=',
    TOKENS['EQUAL-TILDE']: '~=',
    TOKENS['EQUAL-DOUBLE-STAR']: '**=',
    TOKENS['EQUAL-DOUBLE-SLASH']: '//=',
    TOKENS['EQUAL-DOUBLE-LESS-THAN']: '<<=',
    TOKENS['EQUAL-DOUBLE-GREATER-THAN']: '>>=',
    TOKENS['MINUS-GREATER-THAN']: '->',
    TOKENS['EQUAL-ARROW']: '=>',
    TOKENS['EXCLAMATION-GREATER-THAN']: '!>',
    TOKENS['EXCLAMATION-TILDE']: '~!'
})