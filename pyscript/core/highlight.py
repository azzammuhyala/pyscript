from .bases import Pys
from .buffer import PysFileBuffer
from .checks import is_left_parenthesis, is_right_parenthesis, is_parenthesis, is_constant_keywords
from .constants import TOKENS, KEYWORDS, HIGHLIGHT
from .lexer import PysLexer
from .mapping import PARENTHESISES_MAP, HIGHLIGHT_MAP
from .position import PysPosition
from .pysbuiltins import pys_builtins
from .utils.ansi import acolor
from .utils.decorators import typechecked

from html import escape as html_escape
from typing import Callable, Optional

@typechecked
class _HighlightFormatter(Pys):

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

HLFMT_HTML = _HighlightFormatter(
    lambda position, content: '<br>'.join(html_escape(content).splitlines()),
    lambda position, type: f'<span style="color:{HIGHLIGHT_MAP.get(type, "default")}">',
    lambda position, type: '</span>',
    lambda position: '<br>'
)

HLFMT_ANSI = _HighlightFormatter(
    lambda position, content: content,
    _ansi_open_block,
    lambda position, type: '\x1b[0m',
    lambda position: '\n'
)

HLFMT_BBCODE = _HighlightFormatter(
    lambda position, content: content,
    lambda position, type: f'[color={HIGHLIGHT_MAP.get(type, "default")}]',
    lambda position, type: '[/color]',
    lambda position: '\n'
)

@typechecked
def pys_highlight(
    source,
    format: Optional[Callable[[str, PysPosition, str], str]] = None,
    max_parenthesis_level: int = 3
) -> str:
    """
    Highlight a PyScript code from source given.

    Parameters
    ----------
    source: A valid PyScript (Lexer/Tokenize) source code.

    format: A function to format the code form.

    max_parenthesis_level: Maximum difference level of parentheses (with circular indexing).
    """

    file = PysFileBuffer(source)

    if format is None:
        format = HLFMT_HTML

    if max_parenthesis_level < 0:
        raise ValueError("pys_highlight(): max_parenthesis_level must be grather than 0")

    lexer = PysLexer(
        file=file,
        flags=HIGHLIGHT
    )

    tokens, _ = lexer.make_tokens()

    text = file.text
    result = ''
    last_index_position = 0
    parenthesis_level = 0
    parenthesises_level = {
        TOKENS['RIGHT-PARENTHESIS']: 0,
        TOKENS['RIGHT-SQUARE']: 0,
        TOKENS['RIGHT-CURLY']: 0
    }

    for i, token in enumerate(tokens):
        ttype = token.type
        tvalue = token.value

        if is_right_parenthesis(ttype):
            parenthesises_level[ttype] -= 1
            parenthesis_level -= 1

        if ttype == TOKENS['NULL']:
            type_fmt = 'end'

        elif ttype == TOKENS['KEYWORD']:
            type_fmt = 'keyword-constant' if is_constant_keywords(tvalue) else 'keyword'

        elif ttype == TOKENS['IDENTIFIER']:
            obj = pys_builtins.__dict__.get(tvalue, None)

            if isinstance(obj, type):
                type_fmt = 'identifier-type'
            elif callable(obj):
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

        elif is_parenthesis(ttype):
            type_fmt = (
                'invalid'
                if
                    parenthesises_level[PARENTHESISES_MAP.get(ttype, ttype)] < 0 or
                    parenthesis_level < 0
                else
                f'brackets-{parenthesis_level % max_parenthesis_level}'
            )

        elif ttype == TOKENS['NONE']:
            type_fmt = 'invalid'

        else:
            type_fmt = 'default'

        space = text[last_index_position:token.position.start]
        if space:
            result += format('default', PysPosition(file, last_index_position, token.position.start), space)

        result += format(type_fmt, token.position, text[token.position.start:token.position.end])

        if is_left_parenthesis(ttype):
            parenthesises_level[PARENTHESISES_MAP[ttype]] += 1
            parenthesis_level += 1

        elif ttype == TOKENS['NULL']:
            break

        last_index_position = token.position.end

    return result