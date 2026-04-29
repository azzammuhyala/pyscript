import os

PYSCRIPT_PATH = os.path.sep.join(__file__.split(os.path.sep)[:-2])
CORE_PATH = os.path.join(PYSCRIPT_PATH, 'core')
LIBRARIES_PATH = os.path.join(PYSCRIPT_PATH, 'lib')
OTHER_PATH = os.path.join(PYSCRIPT_PATH, 'other')
SITE_PACKAGES_PATH = os.path.join(PYSCRIPT_PATH, 'site-packages')
ICON_PATH = os.path.join(OTHER_PATH, 'PyScript.ico')
GLOBAL_HISTORY_PATH = os.path.join(os.path.expanduser('~'), '.pyscript_history')
GUI_GEOMETRY_PATH = os.path.join(OTHER_PATH, 'gui_geometry.txt')

ENV_PYSCRIPT_NO_EXCEPTHOOK = 'PYSCRIPT_NO_EXCEPTHOOK'
ENV_PYSCRIPT_NO_GIL = 'PYSCRIPT_NO_GIL'
ENV_PYSCRIPT_NO_READLINE = 'PYSCRIPT_NO_READLINE'
ENV_PYSCRIPT_NO_TYPECHECK = 'PYSCRIPT_NO_TYPECHECK'
ENV_PYSCRIPT_NO_COLOR_PROMPT = 'PYSCRIPT_NO_COLOR_PROMPT'
ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE = 'PYSCRIPT_MAXIMUM_TRACEBACK_LINE'
ENV_PYSCRIPT_CLASSIC_LINE_SHELL = 'PYSCRIPT_CLASSIC_LINE_SHELL'
ENV_PYSCRIPT_HISTORY_PATH = 'PYSCRIPT_HISTORY_PATH'
ENV_PYSCRIPT_MAXIMUM_HISTORY_LINE = 'PYSCRIPT_MAXIMUM_HISTORY_LINE'

KEYWORDS = (
    '__debug__', 'False', 'None', 'True', 'and', 'as', 'assert', 'break', 'case', 'catch', 'class', 'constructor',
    'continue', 'default', 'del', 'delete', 'do', 'elif', 'else', 'elseif', 'except', 'extends', 'false', 'finally',
    'for', 'from', 'func', 'function', 'global', 'if', 'import', 'in', 'is', 'match', 'nil', 'none', 'null', 'not',
    'true', 'typeof', 'of', 'or', 'raise', 'repeat', 'return', 'switch', 'throw', 'try', 'until', 'while', 'with'
)

CONSTANT_KEYWORDS = (
    '__debug__', 'False', 'None', 'True', 'and', 'class', 'constructor', 'extends', 'func', 'function', 'false',
    'global', 'in', 'is', 'not', 'nil', 'none', 'null', 'of', 'or', 'true', 'typeof'
)

DEFAULT = 0
NO_COLOR = 1 << 0
DEBUG = 1 << 1
SILENT = 1 << 2
RETURN_RESULT = 1 << 3
DONT_SHOW_BANNER_ON_SHELL = 1 << 4
CLASSIC_LINE_SHELL = 1 << 5
NO_COLOR_PROMPT = 1 << 6
NOTEBOOK = CLASSIC_LINE_SHELL | NO_COLOR_PROMPT

LEXER_HIGHLIGHT = 1 << 0
DICT_TO_JSDICT = 1 << 1