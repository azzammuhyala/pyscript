from os.path import sep, join
from types import MappingProxyType

# paths
PYSCRIPT_PATH = sep.join(__file__.split(sep)[:-2])
CORE_PATH = join(PYSCRIPT_PATH, 'core')
LIBRARIES_PATH = join(PYSCRIPT_PATH, 'lib')
SITE_PACKAGES_PATH = join(PYSCRIPT_PATH, 'site-packages')

# environment variables
PYSCRIPT_TYPECHECKING = 'PYSCRIPT_TYPECHECKING'
PYSCRIPT_EXCEPTHOOK = 'PYSCRIPT_EXCEPTHOOK'
PYSCRIPT_SHELL = 'PYSCRIPT_SHELL'
PYSCRIPT_GIL = 'PYSCRIPT_GIL'

# tokens offset
DOUBLE = 2**8
TRIPLE = 2**9
WITH_EQUAL = 2**10
SPECIAL = 2**11

# tokens
TOKENS = MappingProxyType({
    'NULL': ord('\0'),
    'KEYWORD': 1,
    'IDENTIFIER': 2,
    'NUMBER': 3,
    'STRING': 4,
    'NOT-IN': 5,
    'IS-NOT': 6,
    'NEWLINE': ord('\n'),
    'EXCLAMATION': ord('!'),
    'COMMENT': ord('#'),
    'PERCENT': ord('%'),
    'AMPERSAND': ord('&'),
    'RIGHT-PARENTHESIS': ord(')'),
    'LEFT-PARENTHESIS': ord('('),
    'STAR': ord('*'),
    'PLUS': ord('+'),
    'COMMA': ord(','),
    'MINUS': ord('-'),
    'DOT': ord('.'),
    'SLASH': ord('/'),
    'COLON': ord(':'),
    'SEMICOLON': ord(';'),
    'LESS-THAN': ord('<'),
    'EQUAL': ord('='),
    'GREATER-THAN': ord('>'),
    'QUESTION': ord('?'),
    'AT': ord('@'),
    'LEFT-SQUARE': ord('['),
    'RIGHT-SQUARE': ord(']'),
    'CIRCUMFLEX': ord('^'),
    'LEFT-CURLY': ord('{'),
    'PIPE': ord('|'),
    'RIGHT-CURLY': ord('}'),
    'TILDE': ord('~'),
    'DOUBLE-AMPERSAND': ord('&') + DOUBLE,
    'DOUBLE-STAR': ord('*') + DOUBLE,
    'DOUBLE-PLUS': ord('+') + DOUBLE,
    'DOUBLE-MINUS': ord('-') + DOUBLE,
    'DOUBLE-SLASH': ord('/') + DOUBLE,
    'DOUBLE-LESS-THAN': ord('<') + DOUBLE,
    'DOUBLE-EQUAL': ord('=') + DOUBLE,
    'DOUBLE-GREATER-THAN': ord('>') + DOUBLE,
    'DOUBLE-QUESTION': ord('?') + DOUBLE,
    'DOUBLE-PIPE': ord('|') + DOUBLE,
    'TRIPLE-DOT': ord('.') + TRIPLE,
    'EQUAL-EXCLAMATION': ord('!') + WITH_EQUAL,
    'EQUAL-PERCENT': ord('%') + WITH_EQUAL,
    'EQUAL-AMPERSAND': ord('&') + WITH_EQUAL,
    'EQUAL-STAR': ord('*') + WITH_EQUAL,
    'EQUAL-PLUS': ord('+') + WITH_EQUAL,
    'EQUAL-MINUS': ord('-') + WITH_EQUAL,
    'EQUAL-SLASH': ord('/') + WITH_EQUAL,
    'EQUAL-COLON': ord(':') + WITH_EQUAL,
    'EQUAL-LESS-THAN': ord('<') + WITH_EQUAL,
    'EQUAL-GREATER-THAN': ord('>') + WITH_EQUAL,
    'EQUAL-AT': ord('@') + WITH_EQUAL,
    'EQUAL-CIRCUMFLEX': ord('^') + WITH_EQUAL,
    'EQUAL-PIPE': ord('|') + WITH_EQUAL,
    'EQUAL-TILDE': ord('~') + WITH_EQUAL,
    'EQUAL-DOUBLE-STAR': ord('*') + DOUBLE + WITH_EQUAL,
    'EQUAL-DOUBLE-SLASH': ord('/') + DOUBLE + WITH_EQUAL,
    'EQUAL-DOUBLE-LESS-THAN': ord('<') + DOUBLE + WITH_EQUAL,
    'EQUAL-DOUBLE-GREATER-THAN': ord('>') + DOUBLE + WITH_EQUAL,
    'EXCLAMATION-TILDE': ord('~') + SPECIAL
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
    'delete': 'delete',
    'do': 'do',
    'elif': 'elif',
    'else': 'else',
    'extends': 'extends',
    'finally': 'finally',
    'for': 'for',
    'from': 'from',
    'func': 'func',
    'function': 'function',
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
REVERSE_POW_XOR = 1 << 5