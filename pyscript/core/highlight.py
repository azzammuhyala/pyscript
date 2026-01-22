from .bases import Pys
from .buffer import PysFileBuffer
from .checks import is_left_bracket, is_right_bracket, is_bracket, is_constant_keywords, is_public_attribute
from .constants import TOKENS, KEYWORDS, CONSTANT_KEYWORDS, HIGHLIGHT
from .lexer import PysLexer
from .mapping import BRACKETS_MAP
from .position import PysPosition
from .pysbuiltins import pys_builtins
from .utils.ansi import acolor
from .utils.decorators import typechecked

from html import escape as html_escape
from types import MappingProxyType
from typing import Callable, Optional

HIGHLIGHT_MAP = MappingProxyType({
    'default': '#D4D4D4',
    'keyword': '#C586C0',
    'keyword-constant': '#307CD6',
    'identifier': '#8CDCFE',
    'identifier-constant': '#2EA3FF',
    'identifier-function': '#DCDCAA',
    'identifier-type': '#4EC9B0',
    'number': '#B5CEA8',
    'string': '#CE9178',
    'brackets-0': '#FFD705',
    'brackets-1': '#D45DBA',
    'brackets-2': '#1A9FFF',
    'comment': '#549952',
    'invalid': '#B51819'
})

_builtin_types = frozenset(
    name
    for name, object in pys_builtins.__dict__.items()
    if is_public_attribute(name) and isinstance(object, type)
)

_builtin_functions = frozenset(
    name 
    for name, object in pys_builtins.__dict__.items()
    if is_public_attribute(name) and callable(object)
)

try:
    # if pygments module already exists
    from pygments.lexer import RegexLexer, include, bygroups
    from pygments.style import Style
    from pygments.token import Comment, Error, Escape, Keyword, Name, Number, Operator, Punctuation, String, Whitespace
    from pygments.unistring import xid_start, xid_continue

    _set_keywords = frozenset(KEYWORDS.values())
    _set_constant_keywords = frozenset(CONSTANT_KEYWORDS)
    _set_keyword_definitions = frozenset([
        KEYWORDS['class'],
        KEYWORDS['def'], KEYWORDS['define'], KEYWORDS['func'], KEYWORDS['function']
    ])

    _keywords = '|'.join(_set_keywords)
    _unicode_name = f'[{xid_start}][{xid_continue}]*'
    _dollar_prefix = r'(?:\$(?:[^\S\r\n]*))?'
    _raw_string_prefixes = r'((?:R|r|BR|RB|Br|rB|Rb|bR|br|rb))'
    _string_prefixes = r'((?:B|b)?)'
    _newlines = r'\r\n|\r|\n'

    class PygmentsPyScriptStyle(Pys, Style):

        """
        Pygments style for PyScript language.
        """

        name = 'pyscript'
        aliases = ['pyslang', 'pyscript-programming-language']

        styles = {
            Keyword: HIGHLIGHT_MAP['keyword'],
            Keyword.Constant: HIGHLIGHT_MAP['keyword-constant'],
            Keyword.Codetag: '#1F52B3',
            Name: HIGHLIGHT_MAP['identifier'],
            Name.Variable: HIGHLIGHT_MAP['identifier'],
            Name.Constant: HIGHLIGHT_MAP['identifier-constant'],
            Name.Function: HIGHLIGHT_MAP['identifier-function'],
            Name.Class: HIGHLIGHT_MAP['identifier-type'],
            Number: HIGHLIGHT_MAP['number'],
            String: HIGHLIGHT_MAP['string'],
            String.Affix: '#1F52B3',
            String.Escape: '#D7BA71',
            String.Escape.Invalid: HIGHLIGHT_MAP['invalid'],
            String.Escape.Error: HIGHLIGHT_MAP['invalid'],
            Escape: '#D7BA71',
            Escape.Invalid: HIGHLIGHT_MAP['invalid'],
            Escape.Error: HIGHLIGHT_MAP['invalid'],
            Operator: HIGHLIGHT_MAP['default'],
            Punctuation: HIGHLIGHT_MAP['default'],
            Whitespace: HIGHLIGHT_MAP['default'],
            Comment: HIGHLIGHT_MAP['comment'],
            Error: HIGHLIGHT_MAP['invalid']
        }

    class PygmentsPyScriptLexer(Pys, RegexLexer):

        """
        Pygments lexer for PyScript language.
        """

        name = 'pyscript'
        aliases = ['pyslang', 'pyscript-programming-language']
        filenames = ['*.pys']

        tokens = {

            'root': [
                # Keywords
                (rf'\b({"|".join(_set_keywords ^ _set_constant_keywords)})\b', Keyword),
                (rf'\b({"|".join(_set_constant_keywords ^ _set_keyword_definitions)})\b', Keyword.Constant),

                # Strings
                (
                    _raw_string_prefixes + r"(''')", 
                    bygroups(String.Affix, String.Delimiter), 
                    'raw-string-apostrophe-triple'
                ),
                (
                    _raw_string_prefixes + r'(""")', 
                    bygroups(String.Affix, String.Delimiter), 
                    'raw-string-quotation-triple'
                ),
                (
                    _string_prefixes + r"(''')", 
                    bygroups(String.Affix, String.Delimiter), 
                    'string-apostrophe-triple'
                ),
                (
                    _string_prefixes + r'(""")', 
                    bygroups(String.Affix, String.Delimiter), 
                    'string-quotation-triple'
                ),
                (
                    _raw_string_prefixes + r"(')", 
                    bygroups(String.Affix, String.Delimiter), 
                    'raw-string-apostrophe-single'
                ),
                (
                    _raw_string_prefixes + r'(")', 
                    bygroups(String.Affix, String.Delimiter), 
                    'raw-string-quotation-single'
                ),
                (
                    _string_prefixes + r"(')", 
                    bygroups(String.Affix, String.Delimiter), 
                    'string-apostrophe-single'
                ),
                (
                    _string_prefixes + r'(")', 
                    bygroups(String.Affix, String.Delimiter), 
                    'string-quotation-single'
                ),

                # Numbers
                (
                    r'0[bB][01](_?[01])*[jJiI]?',
                    Number.Bin
                ),
                (
                    r'0[oO][0-7](_?[0-7])*[jJiI]?',
                    Number.Oct
                ),
                (
                    r'0[xX][0-9a-fA-F](_?[0-9a-fA-F])*[jJiI]?',
                    Number.Hex
                ),
                (
                    r'((?:[0-9](_?[0-9])*)?\.[0-9](_?[0-9])*|[0-9](_?[0-9])*\.)([eE][+-]?[0-9](_?[0-9])*)?[jJiI]?|[0-9]'
                    r'(_?[0-9])*([eE][+-]?[0-9](_?[0-9])*)[jJiI]?',
                    Number.Float
                ),
                (
                    r'[0-9](_?[0-9])*[jJiI]?',
                    Number.Integer
                ),

                # Comments
                (r'#', Comment.Single, 'in-comment'),

                # Class definition
                (
                    rf'\b({KEYWORDS["class"]})\b(\s+)(?!{_keywords})({_dollar_prefix}{_unicode_name})',
                    bygroups(Keyword.Constant, Whitespace, Name.Class)
                ),

                # Function definition
                (
                    rf'\b({KEYWORDS["def"]}|{KEYWORDS["define"]}|{KEYWORDS["func"]}|{KEYWORDS["function"]})\b(\s+)'
                    rf'(?!{_keywords})({_dollar_prefix}{_unicode_name})',
                    bygroups(Keyword.Constant, Whitespace, Name.Function)
                ),

                # Keywords (if that definitions is unmatched)
                (rf'\b({"|".join(_set_keyword_definitions)})\b', Keyword.Constant),

                # Built-in types and exceptions
                (
                    rf'{_dollar_prefix}(?:{"|".join(_builtin_types)})',
                    Name.Class.Builtin
                ),

                # Built-in functions
                (
                    rf'{_dollar_prefix}(?:{"|".join(_builtin_functions)})',
                    Name.Function.Builtin
                ),

                # Function calls
                (
                    rf'{_dollar_prefix}{_unicode_name}(?=\s*\()',
                    Name.Function
                ),

                # Constants
                (rf'{_dollar_prefix}(?:[A-Z_]*[A-Z][A-Z0-9_]*)', Name.Constant),

                # Variables
                (rf'{_dollar_prefix}{_unicode_name}', Name.Variable),

                # Whitespaces
                (r'\s+', Whitespace),

                # Punctuation and operators
                (rf'[\(\),;\[\]{{}}]|\\(?:{_newlines})', Punctuation),
                (r'\.\.\.', Keyword.Constant),
                (
                    r'[!%&\*\+\-\./:<=>\?@^\|~]|&&|\*\*|\+\+|--|//|<<|==|>>|\?\?|\|\||!=|%=|&=|\*=|\+=|-=|/=|:=|<=|>=|'
                    r'@=|^=|\|=|~=|\*\*=|//=|<<=|>>=|->|=>|!>|~!', Operator
                ),

                # Invalid tokens
                (r'\\.', Error),
                (r'\$(?:[^\S\r\n]*)(.?)', Error)
            ],

            'code-tags': [
                (r'\b(BUG|FIXME|HACK|NOTE|TODO|XXX)\b', Keyword.Codetag)
            ],

            'string-escapes': [
                (rf'\\([nrtbfav\'"\\]|{_newlines})', String.Escape),
                (r'\\[0-7]{1,3}}', String.Escape.Octal),
                (r'\\x[0-9A-Fa-f]{2}', String.Escape.Hex),
                (r'\\u[0-9A-Fa-f]{4}', String.Escape.Unicode),
                (r'\\U[0-9A-Fa-f]{8}', String.Escape.Unicode),
                (r'\\N\{[^}]+\}', String.Escape.UnicodeName),
                (r'\\.', String.Escape.Error)
            ],

            'raw-string-escapes': [
                (rf'\\([\'"]|{_newlines})', String),
                (r'\\.', String)
            ],

            'raw-string-apostrophe-triple': [
                (r"'''", String.Delimiter, '#pop'),
                include('raw-string-escapes'),
                (rf'{_newlines}|.', String),
            ],

            'raw-string-quotation-triple': [
                (r'"""', String.Delimiter, '#pop'),
                include('raw-string-escapes'),
                (rf'{_newlines}|.', String)
            ],

            'string-apostrophe-triple': [
                (r"'''", String.Delimiter, '#pop'),
                include('string-escapes'),
                include('code-tags'),
                (rf'{_newlines}|.', String)
            ],

            'string-quotation-triple': [
                (r'"""', String.Delimiter, '#pop'),
                include('string-escapes'),
                include('code-tags'),
                (rf'{_newlines}|.', String)
            ],

            'raw-string-apostrophe-single': [
                (r"'", String.Delimiter, '#pop'),
                include('raw-string-escapes'),
                (r'.', String)
            ],

            'raw-string-quotation-single': [
                (r'"', String.Delimiter, '#pop'),
                include('raw-string-escapes'),
                (r'.', String)
            ],

            'string-apostrophe-single': [
                (r"'", String.Delimiter, '#pop'),
                include('string-escapes'),
                include('code-tags'),
                (r'.', String)
            ],

            'string-quotation-single': [
                (r'"', String.Delimiter, '#pop'),
                include('string-escapes'),
                include('code-tags'),
                (r'.', String)
            ],

            'in-comment': [
                (r'$', Comment.Single, '#pop'),
                include('code-tags'),
                (r'.', Comment.Single),
            ]

        }

    del (
        _set_keywords, _set_constant_keywords, _set_keyword_definitions, _keywords, _unicode_name, _dollar_prefix,
        _raw_string_prefixes, _string_prefixes, _newlines
    )

except ImportError as e:
    _error = e

    class PygmentsPyScriptStyle(Pys):
        def __new__(cls, *args, **kwargs):
            raise ImportError(f"cannot import module pygments: {_error}") from _error

    class PygmentsPyScriptLexer(Pys):
        def __new__(cls, *args, **kwargs):
            raise ImportError(f"cannot import module pygments: {_error}") from _error

@typechecked
class _PysHighlightFormatter(Pys):

    def __init__(
        self,
        content_block: Callable[[PysPosition, str], str],
        open_block: Callable[[PysPosition, str], str],
        close_block: Callable[[PysPosition, str], str]
    ) -> None:

        self.content_block = content_block
        self.open_block = open_block
        self.close_block = close_block

        self._type = 'start'
        self._open = False

    def __call__(self, type: str, position: PysPosition, content: str) -> str:
        result = ''

        if type == 'end':
            if self._open:
                result += self.close_block(position, self._type)
                self._open = False
            type = 'start'

        elif type == self._type and self._open:
            result += self.content_block(position, content)

        else:
            if self._open:
                result += self.close_block(position, self._type)

            result += self.open_block(position, type) + self.content_block(position, content)
            self._open = True

        self._type = type
        return result

def _ansi_open_block(position, type):
    color = HIGHLIGHT_MAP.get(type, HIGHLIGHT_MAP['default'])
    return acolor(int(color[i:i+2], 16) for i in range(1, 6, 2))

HLFMT_HTML = _PysHighlightFormatter(
    lambda position, content: html_escape(content).replace('\n', '<br>'),
    lambda position, type: f'<span style="color:{HIGHLIGHT_MAP.get(type, HIGHLIGHT_MAP["default"])}">',
    lambda position, type: '</span>',
)

HLFMT_ANSI = _PysHighlightFormatter(
    lambda position, content: content,
    _ansi_open_block,
    lambda position, type: '\x1b[0m',
)

HLFMT_BBCODE = _PysHighlightFormatter(
    lambda position, content: content,
    lambda position, type: f'[color={HIGHLIGHT_MAP.get(type, HIGHLIGHT_MAP["default"])}]',
    lambda position, type: '[/color]',
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

    if max_bracket_level < 0:
        raise ValueError("pys_highlight(): max_bracket_level must be grather than 0")

    if format is None:
        format = HLFMT_HTML

    lexer = PysLexer(
        file=file,
        parser_flags=HIGHLIGHT
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
                elif previous_token.match(TOKENS['KEYWORD'], KEYWORDS['func'], KEYWORDS['function']):
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