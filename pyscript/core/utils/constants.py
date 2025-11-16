from ..constants import TOKENS, KEYWORDS, NSEQ_DICT, NSEQ_SET, NSEQ_LIST, NSEQ_TUPLE

from operator import (
    is_not,
    eq, ne, lt, gt, le, ge,
    add, sub, mul, truediv, floordiv, pow, matmul, mod, and_, or_, xor, lshift, rshift,
    iadd, isub, imul, itruediv, ifloordiv, ipow, imatmul, imod, iand, ior, ixor, ilshift, irshift,
    pos, neg, inv
)
from types import MappingProxyType

BINARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['NOTIN']: lambda a, b : a not in b,
    TOKENS['ISNOT']: is_not,
    TOKENS['ADD']: add,
    TOKENS['SUB']: sub,
    TOKENS['MUL']: mul,
    TOKENS['DIV']: truediv,
    TOKENS['FDIV']: floordiv,
    TOKENS['POW']: pow,
    TOKENS['AT']: matmul,
    TOKENS['MOD']: mod,
    TOKENS['AND']: and_,
    TOKENS['OR']: or_,
    TOKENS['XOR']: xor,
    TOKENS['LSHIFT']: lshift,
    TOKENS['RSHIFT']: rshift,
    TOKENS['EE']: eq,
    TOKENS['NE']: ne,
    TOKENS['LT']: lt,
    TOKENS['GT']: gt,
    TOKENS['LTE']: le,
    TOKENS['GTE']: ge,
    TOKENS['EADD']: iadd,
    TOKENS['ESUB']: isub,
    TOKENS['EMUL']: imul,
    TOKENS['EDIV']: itruediv,
    TOKENS['EFDIV']: ifloordiv,
    TOKENS['EPOW']: ipow,
    TOKENS['EAT']: imatmul,
    TOKENS['EMOD']: imod,
    TOKENS['EAND']: iand,
    TOKENS['EOR']: ior,
    TOKENS['EXOR']: ixor,
    TOKENS['ELSHIFT']: ilshift,
    TOKENS['ERSHIFT']: irshift,
})

UNARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['ADD']: pos,
    TOKENS['SUB']: neg,
    TOKENS['NOT']: inv
})

KEYWORDS_TO_VALUES_MAP = MappingProxyType({
    KEYWORDS['True']: True,
    KEYWORDS['False']: False,
    KEYWORDS['None']: None,
    KEYWORDS['true']: True,
    KEYWORDS['false']: False,
    KEYWORDS['none']: None
})

PARENTHESISES_ITERABLE_MAP = MappingProxyType({
    NSEQ_TUPLE: TOKENS['LPAREN'],
    NSEQ_LIST: TOKENS['LSQUARE'],
    NSEQ_DICT: TOKENS['LBRACE'],
    NSEQ_SET: TOKENS['LBRACE']
})

PARENTHESISES_MAP = MappingProxyType({
    TOKENS['LPAREN']: TOKENS['RPAREN'],
    TOKENS['LSQUARE']: TOKENS['RSQUARE'],
    TOKENS['LBRACE']: TOKENS['RBRACE']
})

LEFT_PARENTHESISES = set(PARENTHESISES_MAP.keys())
RIGHT_PARENTHESISES = set(PARENTHESISES_MAP.values())
PARENTHESISES = LEFT_PARENTHESISES | RIGHT_PARENTHESISES

KEYWORD_IDENTIFIERS = {
    KEYWORDS['of'], KEYWORDS['in'], KEYWORDS['is'],
    KEYWORDS['and'], KEYWORDS['or'], KEYWORDS['not'],
    KEYWORDS['False'], KEYWORDS['None'], KEYWORDS['True'],
    KEYWORDS['false'], KEYWORDS['none'], KEYWORDS['true']
}

ANSI_NAMES_MAP = MappingProxyType({
    'reset': 0,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'bright-red': 91,
    'bright-green': 92,
    'bright-yellow': 93,
    'bright-blue': 94,
    'bright-magenta': 95,
    'bright-cyan': 96,
    'bright-white': 97
})

HIGHLIGHT = MappingProxyType({
    'default': '#D4D4D4',
    'keyword': '#C586C0',
    'keyword-identifier': '#307CD6',
    'identifier': '#8CDCFE',
    'identifier-const': '#2EA3FF',
    'identifier-call': '#DCDCAA',
    'identifier-class': '#4EC9B0',
    'number': '#B5CEA8',
    'string': '#CE9178',
    'parenthesis-unmatch': '#B51819',
    'parenthesis-0': '#FFD705',
    'parenthesis-1': '#D45DBA',
    'parenthesis-2': '#1A9FFF',
    'comment': '#549952'
})

PYTHON_EXTENSIONS = {
    '.ipy',
    '.py',
    '.pyc',
    '.pyd',
    '.pyi',
    '.pyo',
    '.pyp',
    '.pyw',
    '.pyz',
    '.pyproj',
    '.rpy',
    '.xpy'
}

BLACKLIST_PYTHON_BUILTINS = {
    'compile',
    'copyright',
    'credits',
    'dir',
    'eval',
    'exec',
    'help',
    'globals',
    'license',
    'locals',
    'vars'
}

CONSTRUCTOR_METHODS = ('__new__', '__init__')