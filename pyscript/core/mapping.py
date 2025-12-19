from .constants import TOKENS, KEYWORDS

from operator import (
    is_not, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, floordiv, pow, matmul, mod, and_, or_, xor, lshift, rshift,
    iadd, isub, imul, itruediv, ifloordiv, ipow, imatmul, imod, iand, ior, ixor, ilshift, irshift, pos, neg, inv
)
from types import MappingProxyType

BINARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['NOT-IN']: lambda a, b : a not in b,
    TOKENS['IS-NOT']: is_not,
    TOKENS['PLUS']: add,
    TOKENS['MINUS']: sub,
    TOKENS['STAR']: mul,
    TOKENS['SLASH']: truediv,
    TOKENS['DOUBLE-SLASH']: floordiv,
    TOKENS['DOUBLE-STAR']: pow,
    TOKENS['AT']: matmul,
    TOKENS['PERCENT']: mod,
    TOKENS['AMPERSAND']: and_,
    TOKENS['PIPE']: or_,
    TOKENS['CIRCUMFLEX']: xor,
    TOKENS['DOUBLE-LESS-THAN']: lshift,
    TOKENS['DOUBLE-GREATER-THAN']: rshift,
    TOKENS['DOUBLE-EQUAL']: eq,
    TOKENS['EQUAL-EXCLAMATION']: ne,
    TOKENS['LESS-THAN']: lt,
    TOKENS['GREATER-THAN']: gt,
    TOKENS['EQUAL-LESS-THAN']: le,
    TOKENS['EQUAL-GREATER-THAN']: ge,
    TOKENS['EQUAL-PLUS']: iadd,
    TOKENS['EQUAL-MINUS']: isub,
    TOKENS['EQUAL-STAR']: imul,
    TOKENS['EQUAL-SLASH']: itruediv,
    TOKENS['EQUAL-DOUBLE-SLASH']: ifloordiv,
    TOKENS['EQUAL-DOUBLE-STAR']: ipow,
    TOKENS['EQUAL-AT']: imatmul,
    TOKENS['EQUAL-PERCENT']: imod,
    TOKENS['EQUAL-AMPERSAND']: iand,
    TOKENS['EQUAL-PIPE']: ior,
    TOKENS['EQUAL-CIRCUMFLEX']: ixor,
    TOKENS['EQUAL-DOUBLE-LESS-THAN']: ilshift,
    TOKENS['EQUAL-DOUBLE-GREATER-THAN']: irshift,
})

UNARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['PLUS']: pos,
    TOKENS['MINUS']: neg,
    TOKENS['TILDE']: inv
})

KEYWORDS_TO_VALUES_MAP = MappingProxyType({
    KEYWORDS['True']: True,
    KEYWORDS['False']: False,
    KEYWORDS['None']: None,
    KEYWORDS['true']: True,
    KEYWORDS['false']: False,
    KEYWORDS['none']: None
})

BRACKETS_MAP = MappingProxyType({
    TOKENS['LEFT-PARENTHESIS']: TOKENS['RIGHT-PARENTHESIS'],
    TOKENS['LEFT-SQUARE']: TOKENS['RIGHT-SQUARE'],
    TOKENS['LEFT-CURLY']: TOKENS['RIGHT-CURLY']
})

EMPTY_MAP = MappingProxyType({})