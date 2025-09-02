from .bases import Pys
from .position import PysPositionRange
from .token import PysToken
from .context import PysContext
from .exceptions import PysException
from .constants import TOKENS
from .utils import SYNTAX

from unicodedata import lookup as ulookup

import sys

class PysLexer(Pys):

    def __init__(self, file):
        self.file = file

    def peak(self, index):
        return self.file.text[index] if 0 <= index < len(self.file.text) else None

    def update_current_char(self):
        self.current_char = self.file.text[self.index] if 0 <= self.index < len(self.file.text) else None

    def advance(self):
        if self.error is None:
            self.index += 1
            self.update_current_char()

    def reverse(self, amount):
        if self.error is None:
            self.index -= amount
            self.update_current_char()

    def add_token(self, type, start=None, value=None):
        if self.error is None:

            if start is None:
                start = self.index
                end = self.index + 1
            else:
                end = self.index

            self.tokens.append(PysToken(self.file, type, PysPositionRange(start, end), value))

    def throw(self, start, message):
        if self.error is None:
            self.current_char = None
            self.tokens = None
            self.error = PysException(
                SyntaxError(message),
                PysPositionRange(start, self.index),
                PysContext(None, self.file)
            )

    def is_triple_quote(self, prefix):
        return all(self.peak(self.index + i) == prefix for i in range(3))

    def not_eof(self):
        return self.current_char is not None

    def char_eq(self, character):
        return self.current_char == character

    def char_ne(self, character):
        return self.current_char != character

    def char_in(self, characters):
        return self.not_eof() and self.current_char in characters

    def char_are(self, name_string_method, *args, **kwargs):
        return self.not_eof() and getattr(self.current_char, name_string_method)(*args, **kwargs)

    def make_tokens(self):
        self.index = -1
        self.tokens = []
        self.error = None
        self.current_char = None

        self.advance()

        while self.not_eof():

            if self.char_eq('\n'):
                self.add_token(TOKENS['NEWLINE'])
                self.advance()

            elif self.char_are('isspace'):
                self.advance()

            elif self.char_eq('#'):
                self.skip_comment()

            elif self.char_in('0123456789.'):
                self.make_number()

            elif self.char_are('isidentifier'):
                self.make_identifier()

            elif self.char_eq('$'):
                self.make_dollar()

            elif self.char_in('"\''):
                self.make_string()

            elif self.char_eq('+'):
                self.make_plus()

            elif self.char_eq('-'):
                self.make_minus()

            elif self.char_eq('*'):
                self.make_mul()

            elif self.char_eq('/'):
                self.make_div()

            elif self.char_eq('%'):
                self.make_mod()

            elif self.char_eq('&'):
                self.make_and()

            elif self.char_eq('|'):
                self.make_or()

            elif self.char_eq('^'):
                self.make_xor()

            elif self.char_eq('~'):
                self.make_not()

            elif self.char_eq('!'):
                self.make_not_equal()

            elif self.char_eq('='):
                self.make_equal()

            elif self.char_eq('<'):
                self.make_lt()

            elif self.char_eq('>'):
                self.make_gt()

            elif self.char_eq('('):
                self.add_token(TOKENS['LPAREN'])
                self.advance()

            elif self.char_eq(')'):
                self.add_token(TOKENS['RPAREN'])
                self.advance()

            elif self.char_eq('['):
                self.add_token(TOKENS['LSQUARE'])
                self.advance()

            elif self.char_eq(']'):
                self.add_token(TOKENS['RSQUARE'])
                self.advance()

            elif self.char_eq('{'):
                self.add_token(TOKENS['LBRACE'])
                self.advance()

            elif self.char_eq('}'):
                self.add_token(TOKENS['RBRACE'])
                self.advance()

            elif self.char_eq(','):
                self.add_token(TOKENS['COMMA'])
                self.advance()

            elif self.char_eq(':'):
                self.add_token(TOKENS['COLON'])
                self.advance()

            elif self.char_eq('?'):
                self.add_token(TOKENS['QUESTION'])
                self.advance()

            elif self.char_eq(';'):
                self.add_token(TOKENS['SEMICOLON'])
                self.advance()

            else:
                char = self.current_char
                self.advance()
                self.throw(self.index - 1, "invalid character '{}' (U+{:08X})".format(char, ord(char)))

        self.add_token(TOKENS['EOF'])

        return self.tokens, self.error

    def skip_comment(self):
        self.advance()

        while self.not_eof() and self.char_ne('\n'):
            self.advance()

    def make_number(self):
        start = self.index
        number = ''
        format = int

        is_scientific = False
        is_complex = False
        is_underscore = False

        if self.char_eq('.'):
            format = float
            number = '.'
            self.advance()

        while self.char_in('0123456789'):
            number += self.current_char
            self.advance()

            is_underscore = False

            if self.char_eq('_'):
                is_underscore = True
                self.advance()

            elif self.char_eq('.') and not is_scientific and format is int:
                format = float
                number += '.'
                self.advance()

            elif self.char_in('BOXbox') and not is_scientific:
                if number != '0':
                    self.throw(start, "invalid decimal literal")
                    return

                format = str
                base = self.char_are('lower')

                if base == 'b':
                    base = 2
                    literal = '01'
                elif base == 'o':
                    base = 8
                    literal = '01234567'
                elif base == 'x':
                    base = 16
                    literal = '0123456789ABCDEFabcdef'

                self.advance()

                while self.char_in(literal):
                    number += self.current_char
                    self.advance()

                    is_underscore = False

                    if self.char_eq('_'):
                        is_underscore = True
                        self.advance()

                break

            elif self.char_in('eE'):
                format = float
                is_scientific = True
                number += 'e'

                self.advance()

                if self.char_in('+-'):
                    number += self.current_char
                    self.advance()

            elif self.char_in('jJ'):
                is_complex = True
                self.advance()
                break

        if is_underscore:
            self.throw(self.index - 1, "invalid decimal literal")

        if self.char_eq('.'):
            self.advance()
            if format is float or is_complex or is_scientific:
                self.throw(self.index - 1, "invalid decimal literal")
            format = float

        if self.error is None:

            def wrap(obj, *args):
                result = obj(number, *args)
                return complex(0, result) if is_complex else result

            if format is float:
                if number == '.':
                    self.add_token(TOKENS['DOT'], start)
                else:
                    self.add_token(TOKENS['NUMBER'], start, wrap(float))
            elif format is str:
                self.add_token(TOKENS['NUMBER'], start, wrap(int, base))
            elif format is int:
                self.add_token(TOKENS['NUMBER'], start, wrap(int))

    def make_identifier(self, as_identifier=False, start=None):
        start = start if as_identifier else self.index
        name = ''

        while self.not_eof() and (name + self.current_char).isidentifier():
            name += self.current_char
            self.advance()

        self.add_token(
            TOKENS['KEYWORD'] if not as_identifier and name in SYNTAX['keywords'].values() else TOKENS['IDENTIFIER'],
            start,
            name
        )

    def make_dollar(self):
        start = self.index

        self.advance()

        while self.not_eof() and self.char_ne('\n') and self.char_are('isspace'):
            self.advance()

        if not self.char_are('isidentifier'):
            self.advance()
            self.throw(self.index - 1, "expected identifier")

        self.make_identifier(as_identifier=True, start=start)

    def make_string(self):
        string = ''
        start = self.index
        prefix = self.current_char

        is_triple_quote = self.is_triple_quote(prefix)
        warning_displayed = False
        decoded_error_message = None

        self.advance()

        if is_triple_quote:
            self.advance()
            self.advance()

        while self.not_eof() and not (self.is_triple_quote(prefix) if is_triple_quote else self.char_in(prefix + '\n')):

            if self.char_eq('\\'):
                self.advance()

                if self.char_in('\\\'"nrtbfav\n'):
                    if self.char_in('\\\'"'):
                        string += self.current_char
                    elif self.char_eq('n'):
                        string += '\n'
                    elif self.char_eq('r'):
                        string += '\r'
                    elif self.char_eq('t'):
                        string += '\t'
                    elif self.char_eq('b'):
                        string += '\b'
                    elif self.char_eq('f'):
                        string += '\f'
                    elif self.char_eq('a'):
                        string += '\a'
                    elif self.char_eq('v'):
                        string += '\v'
                    self.advance()

                elif decoded_error_message is None:
                    escape = ''

                    if self.char_in('01234567'):
                        while self.not_eof() and self.char_in('01234567') and len(escape) < 3:
                            escape += self.current_char
                            self.advance()

                        string += chr(int(escape, 8))

                    elif self.char_in('xuU'):
                        if self.current_char == 'x':
                            length = 2
                        elif self.current_char == 'u':
                            length = 4
                        elif self.current_char == 'U':
                            length = 8

                        base = self.current_char

                        self.advance()

                        while self.not_eof() and self.char_in('0123456789ABCDEFabcdef') and len(escape) < length:
                            escape += self.current_char
                            self.advance()

                        if len(escape) != length:
                            decoded_error_message = "codec can't decode bytes, truncated \\{}{} escape".format(base, 'X' * length)
                        else:
                            string += chr(int(escape, 16))

                    elif self.char_eq('N'):
                        self.advance()

                        if self.current_char != '{':
                            decoded_error_message = "malformed \\N character escape"
                            continue

                        self.advance()

                        while self.not_eof() and self.char_ne('}'):
                            escape += self.current_char
                            self.advance()

                        if self.current_char == '}':
                            try:
                                string += ulookup(escape)
                            except KeyError:
                                decoded_error_message = "codec can't decode bytes, unknown Unicode character name"
                            self.advance()
                        else:
                            decoded_error_message = "malformed \\N character escape"

                    else:
                        if not warning_displayed:
                            print("SyntaxWarning: invalid escape sequence '\\{}'".format(self.current_char), file=sys.stderr)
                            warning_displayed = True

                        string += '\\' + self.current_char
                        self.advance()

            else:
                string += self.current_char
                self.advance()

        if not (self.is_triple_quote(prefix) if is_triple_quote else self.char_eq(prefix)):
            self.throw(start, "unterminated string literal")
        elif decoded_error_message:
            self.throw(start, decoded_error_message)

        if is_triple_quote:
            self.advance()
            self.advance()

        self.advance()
        self.add_token(TOKENS['STRING'], start, string)

    def make_plus(self):
        start = self.index
        type = TOKENS['PLUS']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IPLUS']
            self.advance()

        elif self.char_eq('+'):
            type = TOKENS['INCREMENT']
            self.advance()

        self.add_token(type, start)

    def make_minus(self):
        start = self.index
        type = TOKENS['MINUS']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IMINUS']
            self.advance()

        elif self.char_eq('-'):
            type = TOKENS['DECREMENT']
            self.advance()

        self.add_token(type, start)

    def make_mul(self):
        start = self.index
        type = TOKENS['MUL']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IMUL']
            self.advance()

        elif self.char_eq('*'):
            type = TOKENS['POW']
            self.advance()

        if type == TOKENS['POW'] and self.char_eq('='):
            type = TOKENS['IPOW']
            self.advance()

        self.add_token(type, start)

    def make_div(self):
        start = self.index
        type = TOKENS['DIV']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IDIV']
            self.advance()

        elif self.char_eq('/'):
            type = TOKENS['FDIV']
            self.advance()

        if type == TOKENS['FDIV'] and self.char_eq('='):
            type = TOKENS['IFDIV']
            self.advance()

        self.add_token(type, start)

    def make_mod(self):
        start = self.index
        type = TOKENS['MOD']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IMOD']
            self.advance()

        self.add_token(type, start)

    def make_and(self):
        start = self.index
        type = TOKENS['AND']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IAND']
            self.advance()

        self.add_token(type, start)

    def make_or(self):
        start = self.index
        type = TOKENS['OR']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['IOR']
            self.advance()

        self.add_token(type, start)

    def make_xor(self):
        start = self.index
        type = TOKENS['XOR']

        self.advance()

        if self.current_char == '=':
            type = TOKENS['IXOR']
            self.advance()

        self.add_token(type, start)

    def make_not(self):
        start = self.index
        type = TOKENS['NOT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['CE']
            self.advance()

        self.add_token(type, start)

    def make_not_equal(self):
        start = self.index

        self.advance()

        if self.char_ne('='):
            self.advance()
            self.throw(self.index - 1, "expected '='")

        self.advance()
        self.add_token(TOKENS['NE'], start)

    def make_equal(self):
        start = self.index
        type = TOKENS['EQ']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EE']
            self.advance()

        self.add_token(type, start)

    def make_lt(self):
        start = self.index
        type = TOKENS['LT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['LTE']
            self.advance()
        elif self.char_eq('<'):
            type = TOKENS['LSHIFT']
            self.advance()

        if type == TOKENS['LSHIFT'] and self.char_eq('='):
            type = TOKENS['ILSHIFT']
            self.advance()

        self.add_token(type, start)

    def make_gt(self):
        start = self.index
        type = TOKENS['GT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['GTE']
            self.advance()
        elif self.char_eq('>'):
            type = TOKENS['RSHIFT']
            self.advance()

        if type == TOKENS['RSHIFT'] and self.char_eq('='):
            type = TOKENS['IRSHIFT']
            self.advance()

        self.add_token(type, start)