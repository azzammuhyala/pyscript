from .bases import Pys
from .buffer import PysFileBuffer
from .checks import is_left_bracket, is_right_bracket, is_bracket, is_constant_keywords, is_public_attribute
from .constants import TOKENS, KEYWORDS, CONSTANT_KEYWORDS, HIGHLIGHT
from .lexer import PysLexer
from .mapping import BRACKETS_MAP, HIGHLIGHT_MAP
from .position import PysPosition
from .pysbuiltins import pys_builtins
from .utils.ansi import acolor
from .utils.decorators import typechecked

from html import escape as html_escape
from typing import Callable, Optional

_builtin_types = tuple(
    name
    for name, object in pys_builtins.__dict__.items()
    if is_public_attribute(name) and isinstance(object, type)
)

_builtin_functions = tuple(
    name 
    for name, object in pys_builtins.__dict__.items()
    if is_public_attribute(name) and callable(object)
)

try:
    # if pygments module exists
    from pygments.lexer import RegexLexer, include, bygroups
    from pygments.token import Comment, Keyword, Name, Number, String, Text

    _keyword_definitions = (KEYWORDS['class'], KEYWORDS['func'], KEYWORDS['function'])

    class PygmentsPyScriptLexer(Pys, RegexLexer):

        """
        Pygments lexer for PyScript language.
        """

        name = 'PyScript'
        aliases = ['pyscript']
        filenames = ['*.pys']

        tokens = {

            "root": [
                # Keywords
                (
                    rf"\b({'|'.join(keyword for keyword in KEYWORDS if not is_constant_keywords(keyword))})\b",
                    Keyword.Reserved
                ),
                (
                    r"\b(" +
                    '|'.join(keyword for keyword in CONSTANT_KEYWORDS if keyword not in _keyword_definitions) +
                    r")\b",
                    Keyword.Constant
                ),

                # Strings
                (
                    r"((?:[rRbBuU]{1,2})?)(''')", 
                    bygroups(String.Affix, String.Delimiter), 
                    "string-triple-single"
                ),
                (
                    r"((?:[rRbBuU]{1,2})?)(\"\"\")", 
                    bygroups(String.Affix, String.Delimiter), 
                    "string-triple-double"
                ),
                (
                    r"((?:[rRbBuU]{1,2})?)(')", 
                    bygroups(String.Affix, String.Delimiter), 
                    "string-single"
                ),
                (
                    r"((?:[rRbBuU]{1,2})?)(\")", 
                    bygroups(String.Affix, String.Delimiter), 
                    "string-double"
                ),

                # Numbers
                (
                    r"0[bB][01](_?[01])*[jJiI]?|0[oO][0-7](_?[0-7])*[jJiI]?|0[xX][0-9a-fA-F](_?[0-9a-fA-F])*[jJiI]?|((?"
                    r":[0-9](_?[0-9])*)?\\.[0-9](_?[0-9])*|[0-9](_?[0-9])*\\.)([eE][+-]?[0-9](_?[0-9])*)?[jJiI]?|[0-9]("
                    r"_?[0-9])*([eE][+-]?[0-9](_?[0-9])*)[jJiI]?|[0-9](_?[0-9])*[jJiI]?",
                    Number
                ),

                # Comments
                (r"#.*$", Comment.Single),

                # Class definition
                (
                    rf"\b({KEYWORDS['class']})\b(\s*)((?:\$(?:[^\S\r\n]*))?\b[a-zA-Z_][a-zA-Z0-9_]*)\b",
                    bygroups(Keyword.Declaration, Text, Name.Class)
                ),

                # Function definition
                (
                    rf"\b({KEYWORDS['func']}|{KEYWORDS['function']})\b"
                    r"(\s*)((?:\$(?:[^\S\r\n]*))?\b[a-zA-Z_][a-zA-Z0-9_]*)\b",
                    bygroups(Keyword.Declaration, Text, Name.Function)
                ),

                # Keywords (if that definition is unmatched)
                (
                    rf"\b({'|'.join(_keyword_definitions)})\b",
                    Keyword.Constant
                ),

                # Built-in types and exceptions
                (
                    rf"(?:\$(?:[^\S\r\n]*))?(?:{'|'.join(_builtin_types)})\b",
                    Name.Builtin
                ),

                # Built-in functions
                (
                    rf"(?:\$(?:[^\S\r\n]*))?[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()|\b(?:{'|'.join(_builtin_functions)})\b",
                    Name.Builtin
                ),

                # Constants
                (r"(?:\$(?:[^\S\r\n]*))?\b(?:[A-Z_]*[A-Z][A-Z0-9_]*)\b", Name.Constant),

                # Variables
                (r"(?:\$(?:[^\S\r\n]*))?\b[a-zA-Z_][a-zA-Z0-9_]*\b", Name),

            ],

            "string-escape": [
                (r"\\([nrtbfav\\'\"\n\r])", String.Escape),
                (r"\\[0-3][0-7]{0,2}", String.Escape.Octal),
                (r"\\x[0-9A-Fa-f]{2}", String.Escape.Hex),
                (r"\\u[0-9A-Fa-f]{4}", String.Escape.Unicode),
                (r"\\U[0-9A-Fa-f]{8}", String.Escape.Unicode),
                (r"\\N\{[^}]+\}", String.Escape.Unicode),
                (r"\\.", String.Escape.Invalid)
            ],

            "string-single": [
                (r"'", String.Delimiter, "#pop"),
                include("string-escape"),
                (r"[^'\\]+", String),
            ],

            "string-double": [
                (r"\"", String.Delimiter, "#pop"),
                include("string-escape"),
                (r'[^"\\]+', String),
            ],

            "string-triple-single": [
                (r"'''", String.Delimiter, "#pop"),
                include("string-escape"),
                (r"[^\\']+", String),
            ],

            "string-triple-double": [
                (r'"""', String.Delimiter, "#pop"),
                include("string-escape"),
                (r'[^\\"]+', String),
            ]

        }

except ImportError:

    class PygmentsPyScriptLexer(Pys):

        def __new__(cls, *args, **kwargs):
            raise ModuleNotFoundError("pygments is not found")

@typechecked
class _PysHighlightFormatter(Pys):

    def __init__(
        self,
        content_block: Callable[[PysPosition, str], str],
        open_block: Callable[[PysPosition, str], str],
        close_block: Callable[[PysPosition, str], str],
        newline_block: Callable[[PysPosition], str]
    ) -> None:

        self.content_block = content_block
        self.open_block = open_block
        self.close_block = close_block
        self.newline_block = newline_block

        self._type = 'start'
        self._open = False

    def __call__(self, type: str, position: PysPosition, content: str) -> str:
        result = ''

        if type == 'newline':
            if self._open:
                result += self.close_block(position, self._type)
                self._open = False

            result += self.newline_block(position)

        elif type == 'end':
            if self._open:
                result += self.close_block(position, self._type)
                self._open = False

            type = 'start'

        elif type == self._type and self._open:
            result += self.content_block(position, content)

        else:
            if self._open:
                result += self.close_block(position, self._type)

            result += self.open_block(position, type) + \
                      self.content_block(position, content)

            self._open = True

        self._type = type
        return result

def _ansi_open_block(position, type):
    color = HIGHLIGHT_MAP.get(type, 'default')
    return acolor(int(color[i:i+2], 16) for i in range(1, 6, 2))

HLFMT_HTML = _PysHighlightFormatter(
    lambda position, content: '<br>'.join(html_escape(content).splitlines()),
    lambda position, type: f'<span style="color:{HIGHLIGHT_MAP.get(type, "default")}">',
    lambda position, type: '</span>',
    lambda position: '<br>'
)

HLFMT_ANSI = _PysHighlightFormatter(
    lambda position, content: content,
    _ansi_open_block,
    lambda position, type: '\x1b[0m',
    lambda position: '\n'
)

HLFMT_BBCODE = _PysHighlightFormatter(
    lambda position, content: content,
    lambda position, type: f'[color={HIGHLIGHT_MAP.get(type, "default")}]',
    lambda position, type: '[/color]',
    lambda position: '\n'
)

@typechecked
def pys_highlight(
    source,
    format: Optional[Callable[[str, PysPosition, str], str]] = None,
    max_bracket_level: int = 3
) -> str:
    """
    Highlight a PyScript code from source given.

    Parameters
    ----------
    source: A PyScript source code (tolerant of syntax errors).

    format: A function to format the code form.

    max_bracket_level: Maximum difference level of parentheses (with circular indexing).
    """

    file = PysFileBuffer(source)

    if format is None:
        format = HLFMT_HTML

    if max_bracket_level < 0:
        raise ValueError("pys_highlight(): max_bracket_level must be grather than 0")

    lexer = PysLexer(
        file=file,
        flags=HIGHLIGHT
    )

    tokens, _ = lexer.make_tokens()

    text = file.text
    result = ''
    last_index_position = 0
    bracket_level = 0
    brackets_level = {
        TOKENS['RIGHT-PARENTHESIS']: 0,
        TOKENS['RIGHT-SQUARE']: 0,
        TOKENS['RIGHT-CURLY']: 0
    }

    for i, token in enumerate(tokens):
        ttype = token.type
        tvalue = token.value

        if is_right_bracket(ttype):
            brackets_level[ttype] -= 1
            bracket_level -= 1

        if ttype == TOKENS['NULL']:
            type_fmt = 'end'

        elif ttype == TOKENS['KEYWORD']:
            type_fmt = 'keyword-constant' if is_constant_keywords(tvalue) else 'keyword'

        elif ttype == TOKENS['IDENTIFIER']:
            if tvalue in _builtin_types:
                type_fmt = 'identifier-type'
            elif tvalue in _builtin_functions:
                type_fmt = 'identifier-function'
            else:
                j = i - 1
                while j > 0 and tokens[j].type in (TOKENS['NEWLINE'], TOKENS['COMMENT']):
                    j -= 1

                previous_token = tokens[j]
                if previous_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
                    type_fmt = 'identifier-type'
                elif previous_token.matches(TOKENS['KEYWORD'], (KEYWORDS['func'], KEYWORDS['function'])):
                    type_fmt = 'identifier-function'

                else:
                    j = i + 1
                    if (j < len(tokens) and tokens[j].type == TOKENS['LEFT-PARENTHESIS']):
                        type_fmt = 'identifier-function'
                    else:
                        type_fmt = 'identifier-constant' if tvalue.isupper() else 'identifier'

        elif ttype == TOKENS['NUMBER']:
            type_fmt = 'number'

        elif ttype == TOKENS['STRING']:
            type_fmt = 'string'

        elif ttype == TOKENS['NEWLINE']:
            type_fmt = 'newline'

        elif ttype == TOKENS['COMMENT']:
            type_fmt = 'comment'

        elif is_bracket(ttype):
            type_fmt = (
                'invalid'
                if
                    brackets_level[BRACKETS_MAP.get(ttype, ttype)] < 0 or
                    bracket_level < 0
                else
                f'brackets-{bracket_level % max_bracket_level}'
            )

        elif ttype == TOKENS['NONE']:
            type_fmt = 'invalid'

        else:
            type_fmt = 'default'

        space = text[last_index_position:token.position.start]
        if space:
            result += format('default', PysPosition(file, last_index_position, token.position.start), space)

        result += format(type_fmt, token.position, text[token.position.start:token.position.end])

        if is_left_bracket(ttype):
            brackets_level[BRACKETS_MAP[ttype]] += 1
            bracket_level += 1

        elif ttype == TOKENS['NULL']:
            break

        last_index_position = token.position.end

    return result