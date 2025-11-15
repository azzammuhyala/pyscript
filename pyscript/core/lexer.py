from .bases import Pys
from .buffer import PysFileBuffer
from .constants import TOKENS, KEYWORDS, DEFAULT, COMMENT
from .context import PysContext
from .exceptions import PysException
from .position import PysPosition
from .token import PysToken
from .utils.decorators import typechecked

from unicodedata import lookup as unicode_lookup
from typing import Optional
from sys import stderr

class PysLexer(Pys):

    @typechecked
    def __init__(
        self,
        file: PysFileBuffer,
        flags: int = DEFAULT,
        context_parent: Optional[PysContext] = None,
        context_parent_entry_position: Optional[PysPosition] = None
    ):

        self.file = file
        self.flags = flags
        self.context_parent = context_parent
        self.context_parent_entry_position = context_parent_entry_position

    def update_current_character(self):
        self.current_character = self.file.text[self.index] if 0 <= self.index < len(self.file.text) else None

    def advance(self):
        if self.error is None:
            self.index += 1
            self.update_current_character()

    def reverse(self, amount=1):
        if self.error is None:
            self.index -= amount
            self.update_current_character()

    def not_end_of_file(self):
        return self.current_character is not None

    def character_in(self, characters):
        return self.not_end_of_file() and self.current_character in characters

    def character_are(self, string_method, *args, **kwargs):
        return self.not_end_of_file() and getattr(self.current_character, string_method)(*args, **kwargs)

    def add_token(self, type, start=None, value=None):
        if self.error is None:

            if start is None:
                start = self.index
                end = self.index + 1
            else:
                end = self.index

            self.tokens.append(
                PysToken(
                    type,
                    PysPosition(
                        self.file,
                        start,
                        end
                    ),
                    value
                )
            )

    def throw(self, start, message, end=None):
        if self.error is None:
            self.current_character = None
            self.tokens = []

            self.error = PysException(
                SyntaxError(message),
                PysContext(
                    file=self.file,
                    flags=self.flags,
                    parent=self.context_parent,
                    parent_entry_position=self.context_parent_entry_position
                ),
                PysPosition(self.file, start, end or self.index)
            )

    @typechecked
    def make_tokens(self) -> tuple[tuple[PysToken, ...] | tuple[PysToken], PysException | None]:
        self.index = 0
        self.tokens = []
        self.error = None

        self.update_current_character()

        while self.not_end_of_file():

            if self.current_character == '\n':
                self.add_token(TOKENS['NEWLINE'])
                self.advance()

            elif self.current_character == '\\':
                self.make_back_slash()

            elif self.character_are('isspace'):
                self.advance()

            elif self.character_in('0123456789.'):
                self.make_number()

            elif self.character_in('BRbr"\''):
                self.make_string()

            elif self.character_are('isidentifier'):
                self.make_identifier()

            elif self.current_character == '$':
                self.make_dollar()

            elif self.current_character == '+':
                self.make_add()

            elif self.current_character == '-':
                self.make_sub()

            elif self.current_character == '*':
                self.make_mul()

            elif self.current_character == '/':
                self.make_div()

            elif self.current_character == '%':
                self.make_mod()

            elif self.current_character == '@':
                self.make_at()

            elif self.current_character == '&':
                self.make_and()

            elif self.current_character == '|':
                self.make_or()

            elif self.current_character == '^':
                self.make_xor()

            elif self.current_character == '~':
                self.make_not()

            elif self.current_character == '=':
                self.make_equal()

            elif self.current_character == '!':
                self.make_not_equal()

            elif self.current_character == '<':
                self.make_lt()

            elif self.current_character == '>':
                self.make_gt()

            elif self.current_character == '?':
                self.make_question()

            elif self.current_character == '#':
                self.make_comment()

            elif self.current_character == '(':
                self.add_token(TOKENS['LPAREN'])
                self.advance()

            elif self.current_character == ')':
                self.add_token(TOKENS['RPAREN'])
                self.advance()

            elif self.current_character == '[':
                self.add_token(TOKENS['LSQUARE'])
                self.advance()

            elif self.current_character == ']':
                self.add_token(TOKENS['RSQUARE'])
                self.advance()

            elif self.current_character == '{':
                self.add_token(TOKENS['LBRACE'])
                self.advance()

            elif self.current_character == '}':
                self.add_token(TOKENS['RBRACE'])
                self.advance()

            elif self.current_character == ':':
                self.add_token(TOKENS['COLON'])
                self.advance()

            elif self.current_character == ',':
                self.add_token(TOKENS['COMMA'])
                self.advance()

            elif self.current_character == ';':
                self.add_token(TOKENS['SEMICOLON'])
                self.advance()

            else:
                char = self.current_character

                self.advance()
                self.throw(self.index - 1, f"invalid character '{char}' (U+{ord(char):08X})")

        self.add_token(TOKENS['EOF'])

        return tuple(self.tokens), self.error

    def make_back_slash(self):
        self.advance()

        if self.current_character != '\n':
            self.advance()
            self.throw(self.index - 1, "expected newline character")

        self.advance()

    def make_number(self):
        start = self.index

        if self.current_character == '.':
            self.advance()

            if self.file.text[self.index:self.index + 2] == '..':
                self.advance()
                self.advance()
                self.add_token(TOKENS['ELLIPSIS'], start)
                return

            elif not self.character_in('0123456789'):
                self.add_token(TOKENS['DOT'], start)
                return

            format = float
            number = '.'

        else:
            format = int
            number = ''

        is_scientific = False
        is_complex = False
        is_underscore = False

        while self.character_in('0123456789'):
            number += self.current_character
            self.advance()

            is_underscore = False

            if self.current_character == '_':
                is_underscore = True
                self.advance()

            elif self.current_character == '.' and not is_scientific and format is int:
                format = float

                number += '.'
                self.advance()

            elif self.character_in('BOXbox') and not is_scientific:
                if number != '0':
                    self.throw(start, "invalid decimal literal")
                    return

                format = str
                number = ''

                character_base = self.character_are('lower')

                if character_base == 'b':
                    base = 2
                    literal = '01'
                elif character_base == 'o':
                    base = 8
                    literal = '01234567'
                elif character_base == 'x':
                    base = 16
                    literal = '0123456789ABCDEFabcdef'

                self.advance()

                while self.character_in(literal):
                    number += self.current_character
                    self.advance()

                    is_underscore = False

                    if self.current_character == '_':
                        is_underscore = True
                        self.advance()

                if not number:
                    self.advance()
                    self.throw(self.index - 1, "invalid decimal literal")

                break

            elif self.character_in('eE') and not is_scientific:
                format = float
                is_scientific = True

                number += 'e'
                self.advance()

                if self.character_in('+-'):
                    number += self.current_character
                    self.advance()

        if is_underscore or (is_scientific and number.endswith(('e', '-', '+'))):
            self.advance()
            self.throw(self.index - 1, "invalid decimal literal")

        if self.character_in('jJiI'):
            is_complex = True
            self.advance()

        if self.error is None:

            if format is float:
                result = float(number)
            elif format is str:
                result = int(number, base)
            elif format is int:
                result = int(number)

            self.add_token(TOKENS['NUMBER'], start, complex(0, result) if is_complex else result)

    def make_string(self):
        start = self.index
        string = ''

        is_bytes = False
        is_raw = False

        if self.character_in('BRbr'):

            if self.character_in('Bb'):
                is_bytes = True
                self.advance()

            if self.character_in('Rr'):
                is_raw = True
                self.advance()

            if not self.character_in('"\''):
                self.reverse(self.index - start)
                self.make_identifier()
                return

        prefix = self.current_character
        triple_prefix = prefix * 3

        def triple_quote():
            return self.file.text[self.index:self.index + 3] == triple_prefix

        is_triple_quote = triple_quote()
        warning_displayed = False
        decoded_error_message = None

        def decode_error(is_unicode, start, end, message):
            nonlocal decoded_error_message
            if decoded_error_message is None:
                decoded_error_message = (
                    f"(unicode error) 'unicodeescape' codec can't decode bytes in position {start}-{end}: {message}"
                    if is_unicode else
                    f"codec can't decode bytes in position {start}-{end}: {message}"
                )

        self.advance()

        if is_triple_quote:
            self.advance()
            self.advance()
            start_string = self.index

        else:
            start_string = self.index

        while self.not_end_of_file() and not (triple_quote() if is_triple_quote else self.character_in(prefix + '\n')):

            if self.current_character == '\\':
                start_escape = self.index - start_string

                self.advance()

                if is_raw:
                    string += '\\'

                    if self.character_in('\\\'"\n'):
                        string += self.current_character
                        self.advance()

                elif self.character_in('\\\'"nrtbfav\n'):

                    if self.character_in('\\\'"'):
                        string += self.current_character
                    elif self.current_character == 'n':
                        string += '\n'
                    elif self.current_character == 'r':
                        string += '\r'
                    elif self.current_character == 't':
                        string += '\t'
                    elif self.current_character == 'b':
                        string += '\b'
                    elif self.current_character == 'f':
                        string += '\f'
                    elif self.current_character == 'a':
                        string += '\a'
                    elif self.current_character == 'v':
                        string += '\v'

                    self.advance()

                elif decoded_error_message is None:
                    escape = ''

                    if self.character_in('01234567'):

                        while self.character_in('01234567') and len(escape) < 3:
                            escape += self.current_character
                            self.advance()

                        string += chr(int(escape, 8))

                    elif self.character_in('xuU'):
                        base = self.current_character

                        if base == 'x':
                            length = 2
                        elif base == 'u':
                            length = 4
                        elif base == 'U':
                            length = 8

                        end_escape = self.index - start_string

                        self.advance()

                        while self.character_in('0123456789ABCDEFabcdef') and len(escape) < length:
                            escape += self.current_character
                            self.advance()

                        if len(escape) != length:
                            decode_error(
                                False, start_escape, end_escape,
                                f"truncated \\{base}{'X' * length} escape"
                            )

                        else:
                            try:
                                string += chr(int(escape, 16))
                            except (ValueError, OverflowError):
                                decode_error(
                                    False, start_escape, self.index - start_string,
                                    "illegal Unicode character"
                                )

                    elif self.current_character == 'N':
                        end_escape = self.index - start_string

                        self.advance()

                        if self.current_character != '{':
                            decode_error(
                                True, start_escape, end_escape,
                                "malformed \\N character escape"
                            )
                            continue

                        self.advance()

                        while self.not_end_of_file() and self.current_character != '}':
                            escape += self.current_character
                            self.advance()

                        if self.current_character == '}':
                            try:
                                string += unicode_lookup(escape)
                            except KeyError:
                                decode_error(
                                    True, start_escape, self.index - start_string,
                                    "unknown Unicode character name"
                                )

                            self.advance()

                        else:
                            decode_error(
                                True, start_escape, end_escape,
                                "malformed \\N character escape"
                            )

                    else:
                        if not self.not_end_of_file():
                            string += '\\'
                            break

                        if not warning_displayed:
                            warning_displayed = True
                            print(
                                f"SyntaxWarning: invalid escape sequence '\\{self.current_character}'",
                                file=stderr
                            )

                        string += '\\' + self.current_character
                        self.advance()

            else:
                string += self.current_character
                self.advance()

        if not (triple_quote() if is_triple_quote else self.current_character == prefix):
            self.throw(
                start,
                "unterminated bytes literal" if is_bytes else "unterminated string literal",
                start + 1
            )

        elif decoded_error_message is not None:
            self.advance()
            self.throw(start, decoded_error_message)

        else:
            self.advance()

            if is_triple_quote:
                self.advance()
                self.advance()

            if is_bytes:
                try:
                    string = string.encode('ascii')
                except UnicodeEncodeError:
                    self.throw(start, "invalid bytes literal")

            self.add_token(TOKENS['STRING'], start, string)

    def make_identifier(self, as_identifier=False, start=None):
        start = start if as_identifier else self.index
        name = ''

        while self.not_end_of_file() and (name + self.current_character).isidentifier():
            name += self.current_character
            self.advance()

        self.add_token(
            TOKENS['KEYWORD'] if not as_identifier and name in KEYWORDS.values() else TOKENS['IDENTIFIER'],
            start,
            name
        )

    def make_dollar(self):
        start = self.index

        self.advance()

        while self.not_end_of_file() and self.current_character != '\n' and self.character_are('isspace'):
            self.advance()

        if not self.character_are('isidentifier'):
            self.advance()
            self.throw(self.index - 1, "expected identifier")

        self.make_identifier(as_identifier=True, start=start)

    def make_add(self):
        start = self.index
        type = TOKENS['ADD']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EADD']
            self.advance()

        elif self.current_character == '+':
            type = TOKENS['INCREMENT']
            self.advance()

        self.add_token(type, start)

    def make_sub(self):
        start = self.index
        type = TOKENS['SUB']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['ESUB']
            self.advance()

        elif self.current_character == '-':
            type = TOKENS['DECREMENT']
            self.advance()

        self.add_token(type, start)

    def make_mul(self):
        start = self.index
        type = TOKENS['MUL']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EMUL']
            self.advance()

        elif self.current_character == '*':
            type = TOKENS['POW']
            self.advance()

        if type == TOKENS['POW'] and self.current_character == '=':
            type = TOKENS['EPOW']
            self.advance()

        self.add_token(type, start)

    def make_div(self):
        start = self.index
        type = TOKENS['DIV']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EDIV']
            self.advance()

        elif self.current_character == '/':
            type = TOKENS['FDIV']
            self.advance()

        if type == TOKENS['FDIV'] and self.current_character == '=':
            type = TOKENS['EFDIV']
            self.advance()

        self.add_token(type, start)

    def make_mod(self):
        start = self.index
        type = TOKENS['MOD']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EMOD']
            self.advance()

        self.add_token(type, start)

    def make_at(self):
        start = self.index
        type = TOKENS['AT']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EAT']
            self.advance()

        self.add_token(type, start)

    def make_and(self):
        start = self.index
        type = TOKENS['AND']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EAND']
            self.advance()

        elif self.current_character == '&':
            type = TOKENS['CAND']
            self.advance()

        self.add_token(type, start)

    def make_or(self):
        start = self.index
        type = TOKENS['OR']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EOR']
            self.advance()

        elif self.current_character == '|':
            type = TOKENS['COR']
            self.advance()

        self.add_token(type, start)

    def make_xor(self):
        start = self.index
        type = TOKENS['XOR']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EXOR']
            self.advance()

        self.add_token(type, start)

    def make_not(self):
        start = self.index
        type = TOKENS['NOT']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['CE']
            self.advance()
        elif self.current_character == '!':
            type = TOKENS['NCE']
            self.advance()

        self.add_token(type, start)

    def make_equal(self):
        start = self.index
        type = TOKENS['EQ']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['EE']
            self.advance()

        self.add_token(type, start)

    def make_not_equal(self):
        start = self.index
        type = TOKENS['CNOT']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['NE']
            self.advance()

        self.add_token(type, start)

    def make_lt(self):
        start = self.index
        type = TOKENS['LT']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['LTE']
            self.advance()
        elif self.current_character == '<':
            type = TOKENS['LSHIFT']
            self.advance()

        if type == TOKENS['LSHIFT'] and self.current_character == '=':
            type = TOKENS['ELSHIFT']
            self.advance()

        self.add_token(type, start)

    def make_gt(self):
        start = self.index
        type = TOKENS['GT']

        self.advance()

        if self.current_character == '=':
            type = TOKENS['GTE']
            self.advance()
        elif self.current_character == '>':
            type = TOKENS['RSHIFT']
            self.advance()

        if type == TOKENS['RSHIFT'] and self.current_character == '=':
            type = TOKENS['ERSHIFT']
            self.advance()

        self.add_token(type, start)

    def make_question(self):
        start = self.index
        type = TOKENS['QUESTION']

        self.advance()

        if self.current_character == '?':
            type = TOKENS['NULLISH']
            self.advance()

        self.add_token(type, start)

    def make_comment(self):
        start = self.index
        comment = ''

        self.advance()

        while self.not_end_of_file() and self.current_character != '\n':
            comment += self.current_character
            self.advance()

        if self.flags & COMMENT:
            self.add_token(TOKENS['COMMENT'], start, comment)