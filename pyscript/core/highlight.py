from .bases import Pys
from .buffer import PysFileBuffer
from .constants import TOKENS, KEYWORDS, HIGHLIGHT, SILENT, COMMENT
from .lexer import PysLexer
from .position import PysPosition
from .pysbuiltins import pys_builtins
from .utils import (
    parenthesises_map,
    left_parenthesises,
    right_parenthesises,
    parenthesises,
    highlight_keyword_identifiers
)

from html import escape as html_escape

class _HighlightFormatter(Pys):

    def __init__(self, content_block, open_block, close_block, newline_block):
        self.content_block = content_block
        self.open_block = open_block
        self.close_block = close_block
        self.newline_block = newline_block

        self._type = 'start'
        self._open = False

    def __call__(self, type, position, content):
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

            result += self.open_block(position, type) + self.content_block(position, content)

            self._open = True

        self._type = type
        return result

def _ansi_open_block(position, type):
    color = HIGHLIGHT.get(type, 'default')

    return '\x1b[38;2;{};{};{}m'.format(
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16)
    )

HLFMT_HTML = _HighlightFormatter(
    lambda position, content: '<br>'.join(html_escape(content).splitlines()),
    lambda position, type: '<span style="color:{}">'.format(HIGHLIGHT.get(type, 'default')),
    lambda position, type: '</span>',
    lambda position: '<br>'
)

HLFMT_ANSI = _HighlightFormatter(
    lambda position, content: content,
    _ansi_open_block,
    lambda position, type: '\x1b[0m',
    lambda position: '\n'
)

def pys_highlight(source, format=None, max_parenthesis_level=3, flags=COMMENT):
    """
    Highlight a PyScript code from source given.

    Parameters
    ----------
    source: A valid PyScript (Lexer/Tokenize) source code.

    format: A function to format the code form.

    max_parenthesis_level: Maximum difference level of parentheses (with circular indexing).

    flags: A special flags.
    """

    file = PysFileBuffer(source)

    if format is None:
        format = HLFMT_HTML
    elif not callable(format):
        raise TypeError("pys_highlight(): format must be callable")

    if not isinstance(max_parenthesis_level, int):
        raise TypeError("pys_highlight(): max_parenthesis_level must be integer")
    elif max_parenthesis_level < 0:
        raise ValueError("pys_highlight(): max_parenthesis_level must be grather than 0")

    if not isinstance(flags, int):
        raise TypeError("pys_highlight(): flags must be integer")

    lexer = PysLexer(
        file=file,
        flags=flags
    )

    tokens, error = lexer.make_tokens()
    if error and not (flags & SILENT):
        raise error.exception

    result = ''
    last_index = 0
    parenthesis_level = 0
    parenthesises_level = {
        TOKENS['RPAREN']: 0,
        TOKENS['RSQUARE']: 0,
        TOKENS['RBRACE']: 0
    }

    text = file.text

    for i, token in enumerate(tokens):
        ttype = token.type

        if ttype in right_parenthesises:
            parenthesises_level[ttype] -= 1
            parenthesis_level -= 1

        if ttype == TOKENS['EOF']:
            type_fmt = 'end'

        elif ttype == TOKENS['KEYWORD']:
            type_fmt = 'keyword-identifier' if token.value in highlight_keyword_identifiers else 'keyword'

        elif ttype == TOKENS['NUMBER']:
            type_fmt = 'number'

        elif ttype == TOKENS['STRING']:
            type_fmt = 'string'

        elif ttype == TOKENS['IDENTIFIER']:
            obj = getattr(pys_builtins, token.value, None)

            if isinstance(obj, type):
                type_fmt = 'identifier-class'

            elif callable(obj):
                type_fmt = 'identifier-call'

            else:
                type_fmt = 'identifier-const' if token.value.isupper() else 'identifier'

                j = i + 1
                if (j < len(tokens) and tokens[j].type == TOKENS['LPAREN']):
                    type_fmt = 'identifier-call'

                j = i - 1
                while j > 0 and tokens[j].type == TOKENS['NEWLINE']:
                    j -= 1

                if tokens[j].match(TOKENS['KEYWORD'], KEYWORDS['class']):
                    type_fmt = 'identifier-class'
                elif tokens[j].match(TOKENS['KEYWORD'], KEYWORDS['func']):
                    type_fmt = 'identifier-call'

        elif ttype in parenthesises:
            type_fmt = 'parenthesis-{}'.format(
                'unmatch'
                if
                    parenthesises_level[parenthesises_map.get(ttype, ttype)] < 0 or
                    parenthesis_level < 0
                else
                parenthesis_level % max_parenthesis_level
            )

        elif ttype == TOKENS['NEWLINE']:
            type_fmt = 'newline'

        elif ttype == TOKENS['COMMENT']:
            type_fmt = 'comment'

        else:
            type_fmt = 'default'

        space = text[last_index:token.position.start]
        if space:
            result += format('default', PysPosition(file, last_index, token.position.start), space)

        result += format(type_fmt, token.position, text[token.position.start:token.position.end])

        if ttype in left_parenthesises:
            parenthesises_level[parenthesises_map[ttype]] += 1
            parenthesis_level += 1

        elif ttype == TOKENS['EOF']:
            break

        last_index = token.position.end

    return result