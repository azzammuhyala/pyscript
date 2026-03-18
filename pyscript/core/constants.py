from types import MappingProxyType

import os

# paths
PYSCRIPT_PATH = os.path.sep.join(__file__.split(os.path.sep)[:-2])
CORE_PATH = os.path.join(PYSCRIPT_PATH, 'core')
LIBRARIES_PATH = os.path.join(PYSCRIPT_PATH, 'lib')
OTHER_PATH = os.path.join(PYSCRIPT_PATH, 'other')
SITE_PACKAGES_PATH = os.path.join(PYSCRIPT_PATH, 'site-packages')
ICON_PATH = os.path.join(OTHER_PATH, 'PyScript.ico')

# environment variables
ENV_PYSCRIPT_NO_EXCEPTHOOK = 'PYSCRIPT_NO_EXCEPTHOOK'
ENV_PYSCRIPT_NO_GIL = 'PYSCRIPT_NO_GIL'
ENV_PYSCRIPT_NO_READLINE = 'PYSCRIPT_NO_READLINE'
ENV_PYSCRIPT_NO_TYPECHECK = 'PYSCRIPT_NO_TYPECHECK'
ENV_PYSCRIPT_NO_COLOR_PROMPT = 'PYSCRIPT_NO_COLOR_PROMPT'
ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE = 'PYSCRIPT_MAXIMUM_TRACEBACK_LINE'
ENV_PYSCRIPT_CLASSIC_LINE_SHELL = 'PYSCRIPT_CLASSIC_LINE_SHELL'
ENV_PYSCRIPT_HISTORY_PATH = 'PYSCRIPT_HISTORY_PATH'
ENV_PYSCRIPT_MAXIMUM_HISTORY_LINE = 'PYSCRIPT_MAXIMUM_HISTORY_LINE'

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
    'NOT_IN': 5,
    'IS_NOT': 6,
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
    'EXCLAMATION_TILDE': ord('~') + SPECIAL
})

# keywords
KEYWORDS = (
    '__debug__', 'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'case', 'catch', 'class', 'constructor',
    'continue', 'def', 'default', 'define', 'del', 'delete', 'do', 'elif', 'else', 'elseif', 'except', 'extends',
    'false', 'finally', 'for', 'from', 'func', 'function', 'global', 'if', 'import', 'in', 'is', 'match', 'nil', 'none',
    'null', 'not', 'true', 'typeof', 'of', 'or', 'raise', 'repeat', 'return', 'switch', 'throw', 'try', 'until',
    'while', 'with'
)

CONSTANT_KEYWORDS = (
    '__debug__', 'False', 'None', 'True', 'and', 'class', 'constructor', 'def', 'define', 'extends', 'func', 'function',
    'false', 'global', 'in', 'is', 'not', 'nil', 'none', 'null', 'of', 'or', 'true', 'typeof'
)

# flags
DEFAULT = 0
NO_COLOR = 1 << 0
DEBUG = 1 << 1
SILENT = 1 << 2
RETURN_RESULT = 1 << 3
DONT_SHOW_BANNER_ON_SHELL = 1 << 4
CLASSIC_LINE_SHELL = 1 << 5
NO_COLOR_PROMPT = 1 << 6
NOTEBOOK = CLASSIC_LINE_SHELL | NO_COLOR_PROMPT

# parser flags
LEXER_HIGHLIGHT = 1 << 0
DICT_TO_JSDICT = 1 << 1