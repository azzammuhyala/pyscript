from os.path import sep
from types import MappingProxyType

# paths
PYSCRIPT_PATH = sep.join(__file__.split(sep)[:-2])
LIBRARY_PATH = f'{PYSCRIPT_PATH}{sep}lib'

# tokens offset
DOUBLE = 0xFF * 1
TRIPLE = 0xFF * 2
WITH_EQ = 0xFF * 3
SPECIAL = 0xFF * 4

# tokens
TOKENS = MappingProxyType({
    'EOF': ord('\0'),
    'KEYWORD': 1,
    'IDENTIFIER': 2,
    'NUMBER': 3,
    'STRING': 4,
    'NOTIN': 5,
    'ISNOT': 6,
    'ADD': ord('+'),
    'SUB': ord('-'),
    'MUL': ord('*'),
    'DIV': ord('/'),
    'FDIV': ord('/') + DOUBLE,
    'MOD': ord('%'),
    'AT': ord('@'),
    'POW': ord('*') + DOUBLE,
    'AND': ord('&'),
    'OR': ord('|'),
    'XOR': ord('^'),
    'NOT': ord('~'),
    'LSHIFT': ord('<') + DOUBLE,
    'RSHIFT': ord('>') + DOUBLE,
    'INCREMENT': ord('+') + DOUBLE,
    'DECREMENT': ord('-') + DOUBLE,
    'CAND': ord('&') + DOUBLE,
    'COR': ord('|') + DOUBLE,
    'CNOT': ord('!'),
    'LPAREN': ord('('),
    'RPAREN': ord(')'),
    'LSQUARE': ord('['),
    'RSQUARE': ord(']'),
    'LBRACE': ord('{'),
    'RBRACE': ord('}'),
    'EQ': ord('='),
    'EE': ord('=') + DOUBLE,
    'NE': ord('!') + WITH_EQ,
    'CE': ord('~') + WITH_EQ,
    'NCE': ord('~') + SPECIAL,
    'LT': ord('<'),
    'GT': ord('>'),
    'LTE': ord('<') + WITH_EQ,
    'GTE': ord('>') + WITH_EQ,
    'EADD': ord('+') + WITH_EQ,
    'ESUB': ord('-') + WITH_EQ,
    'EMUL': ord('*') + WITH_EQ,
    'EDIV': ord('/') + WITH_EQ,
    'EFDIV': ord('/') + DOUBLE + WITH_EQ,
    'EMOD': ord('%') + WITH_EQ,
    'EAT': ord('@') + WITH_EQ,
    'EPOW': ord('*') + DOUBLE + WITH_EQ,
    'EAND': ord('&') + WITH_EQ,
    'EOR': ord('|') + WITH_EQ,
    'EXOR': ord('^') + WITH_EQ,
    'ELSHIFT': ord('<') + DOUBLE + WITH_EQ,
    'ERSHIFT': ord('>') + DOUBLE + WITH_EQ,
    'NULLISH': ord('?') + DOUBLE,
    'COLON': ord(':'),
    'COMMA': ord(','),
    'DOT': ord('.'),
    'QUESTION': ord('?'),
    'ELLIPSIS': ord('.') + TRIPLE,
    'SEMICOLON': ord(';'),
    'NEWLINE': ord('\n'),
    'COMMENT': ord('#')
})

# keywords
KEYWORDS = MappingProxyType({
    '__debug__': '__debug__',
    'False': 'False',
    'None': 'None',
    'True': 'True',
    'false': 'false',
    'none': 'none',
    'true': 'true',
    'and': 'and',
    'as': 'as',
    'assert': 'assert',
    'break': 'break',
    'case': 'case',
    'catch': 'catch',
    'class': 'class',
    'continue': 'continue',
    'default': 'default',
    'del': 'del',
    'do': 'do',
    'elif': 'elif',
    'else': 'else',
    'extends': 'extends',
    'finally': 'finally',
    'for': 'for',
    'from': 'from',
    'func': 'func',
    'global': 'global',
    'if': 'if',
    'import': 'import',
    'in': 'in',
    'is': 'is',
    'not': 'not',
    'of': 'of',
    'or': 'or',
    'return': 'return',
    'switch': 'switch',
    'throw': 'throw',
    'try': 'try',
    'while': 'while',
    'with': 'with'
})

# flags
DEFAULT = 0
DEBUG = 1 << 0
SILENT = 1 << 1
RETRES = 1 << 2
COMMENT = 1 << 3
NO_COLOR = 1 << 4
REVERSE_POW_XOR = 1 << 10

# styles for pyscript.core.utils.general.acolor
BOLD = 1 << 0
ITALIC = 1 << 1
UNDER = 1 << 2
STRIKET = 1 << 3

# types for pyscript.core.nodes.PysSequenceNode
NSEQ_STATEMENTS = 1
NSEQ_GLOBAL = 2
NSEQ_DEL = 3
NSEQ_DICT = 4
NSEQ_SET = 5
NSEQ_LIST = 6
NSEQ_TUPLE = 7

# styles for pyscript.core.nodes.PysTernaryOperatorNode
NTER_GENERAL = 1
NTER_PYTHONIC = 2

# operand positions for pyscript.core.nodes.PysUnaryOperatorNode
NUNR_LEFT = 1
NUNR_RIGHT = 2

# all packages for pyscript.core.nodes.PysImportNode
NIMP_ALL = 1