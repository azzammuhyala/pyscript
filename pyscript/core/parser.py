from .bases import Pys
from .constants import (
    TOKENS, KEYWORDS,
    DEFAULT, REVERSE_POW_XOR,
    NSEQ_STATEMENTS, NSEQ_GLOBAL, NSEQ_DEL, NSEQ_DICT, NSEQ_SET, NSEQ_LIST, NSEQ_TUPLE,
    NTER_GENERAL, NTER_PYTHONIC,
    NUNR_LEFT, NUNR_RIGHT,
    NIMP_ALL
)
from .context import PysContext
from .exceptions import PysException
from .nodes import *
from .position import PysPosition
from .results import PysParserResult
from .token import PysToken
from .utils.decorators import typechecked
from .utils.constants import PARENTHESISES_ITERABLE_MAP, PARENTHESISES_MAP, RIGHT_PARENTHESISES

from typing import Optional, Callable

class PysParser(Pys):

    @typechecked
    def __init__(
        self,
        tokens: tuple[PysToken, ...] | tuple[PysToken],
        flags: int = DEFAULT,
        context_parent: Optional[PysContext] = None,
        context_parent_entry_position: Optional[PysPosition] = None
    ):
        self.tokens = tokens
        self.flags = flags
        self.context = context_parent
        self.context_parent_entry_position = context_parent_entry_position

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def advance(self):
        self.token_index += 1
        self.update_current_token()

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()

    def error(self, message, position=None):
        return PysException(
            SyntaxError(message),
            PysContext(
                file=self.tokens[0].position.file,
                flags=self.flags,
                parent=self.context,
                parent_entry_position=self.context_parent_entry_position
            ),
            position or self.current_token.position
        )

    @typechecked
    def parse(self, func: Optional[Callable[[], PysParserResult]] = None) -> PysParserResult:
        self.token_index = 0
        self.parenthesis_level = 0

        self.update_current_token()

        result = (func or self.statements)()

        if not result.error:
            if self.current_token.type in RIGHT_PARENTHESISES:
                return result.failure(self.error(f"unmatched {chr(self.current_token.type)!r}"))
            elif self.current_token.type != TOKENS['EOF']:
                return result.failure(self.error("invalid syntax"))

        return result

    def statements(self):
        result = PysParserResult()
        start = self.current_token.position.start

        statements = []
        more_statements = True
        parenthesis_level = self.parenthesis_level

        self.parenthesis_level = 0

        while True:
            advance_count = self.skip(result, (TOKENS['NEWLINE'], TOKENS['SEMICOLON']))

            if not more_statements:
                if advance_count == 0:
                    break
                more_statements = True

            statement = result.try_register(self.statement())
            if result.error:
                return result

            if statement:
                statements.append(statement)
            else:
                self.reverse(result.to_reverse_count)

            more_statements = False

        self.parenthesis_level = parenthesis_level

        return result.success(
            PysSequenceNode(
                NSEQ_STATEMENTS,
                statements,
                PysPosition(
                    self.tokens[0].position.file,
                    start,
                    self.current_token.position.end
                )
            )
        )

    def statement(self):
        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['from']):
            return self.from_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return self.import_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['if']):
            return self.if_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['switch']):
            return self.switch_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['try']):
            return self.try_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['with']):
            return self.with_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['for']):
            return self.for_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return self.while_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['do']):
            return self.do_while_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
            return self.class_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['return']):
            return self.return_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['global']):
            return self.global_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['del']):
            return self.del_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['throw']):
            return self.throw_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['assert']):
            return self.assert_expr()

        elif self.current_token.type == TOKENS['AT']:
            return self.decorator_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['continue']):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysContinueNode(position))

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['break']):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysBreakNode(position))

        result = PysParserResult()

        assign_expr = result.register(self.assign_expr())
        if result.error:
            return result.failure(self.error("expected an expression or statement"), fatal=False)

        return result.success(assign_expr)

    def expr(self):
        result = PysParserResult()

        node = result.register(self.single_expr())
        if result.error:
            return result

        if self.current_token.type == TOKENS['COMMA']:
            elements = [node]

            while self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                element = result.try_register(self.single_expr())
                if result.error:
                    return result

                if element:
                    elements.append(element)
                else:
                    self.reverse(result.to_reverse_count)
                    break

            self.skip_expr(result)

            return result.success(
                PysSequenceNode(
                    NSEQ_TUPLE,
                    elements,
                    PysPosition(
                        self.tokens[0].position.file,
                        node.position.start,
                        elements[-1].position.end
                    )
                )
            )

        return result.success(node)

    def single_expr(self):
        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
            return self.func_expr()

        return self.ternary()

    def ternary(self):
        result = PysParserResult()

        node = result.register(self.nullish())
        if result.error:
            return result

        if self.current_token.type == TOKENS['QUESTION']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            valid = result.register(self.ternary(), True)
            if result.error:
                return result

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            invalid = result.register(self.ternary(), True)
            if result.error:
                return result

            return result.success(
                PysTernaryOperatorNode(
                    node,
                    valid,
                    invalid,
                    style=NTER_GENERAL
                )
            )

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['if']):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            condition = result.register(self.ternary(), True)
            if result.error:
                return result

            if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
                return result.failure(self.error(f"expected {KEYWORDS['else']!r}"))

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            invalid = result.register(self.ternary(), True)
            if result.error:
                return result

            return result.success(
                PysTernaryOperatorNode(
                    condition,
                    node,
                    invalid,
                    style=NTER_PYTHONIC
                )
            )

        return result.success(node)

    def nullish(self):
        return self.binary_operator(self.logic, (TOKENS['NULLISH'],))

    def logic(self):
        return self.binary_operator(
            self.member,
            (
                (TOKENS['KEYWORD'], KEYWORDS['and']),
                (TOKENS['KEYWORD'], KEYWORDS['or']),
                TOKENS['CAND'], TOKENS['COR']
            )
        )

    def member(self):
        return self.chain_operator(
            self.comp,
            (
                (TOKENS['KEYWORD'], KEYWORDS['in']),
                (TOKENS['KEYWORD'], KEYWORDS['is']),
                (TOKENS['KEYWORD'], KEYWORDS['not'])
            ),
            is_member=True
        )

    def comp(self):
        token = self.current_token

        if token.match(TOKENS['KEYWORD'], KEYWORDS['not']) or token.type == TOKENS['CNOT']:
            result = PysParserResult()

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = result.register(self.comp(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node,
                    operand_position=NUNR_LEFT
                )
            )

        return self.chain_operator(
            self.bitwise,
            (
                TOKENS['EE'], TOKENS['NE'], TOKENS['CE'], TOKENS['NCE'],
                TOKENS['LT'], TOKENS['GT'], TOKENS['LTE'], TOKENS['GTE']
            )
        )

    def bitwise(self):
        return self.binary_operator(
            self.arith,
            (
                TOKENS['AND'], TOKENS['OR'],
                TOKENS['POW'] if self.flags & REVERSE_POW_XOR else TOKENS['XOR'],
                TOKENS['LSHIFT'], TOKENS['RSHIFT']
            ),
            is_bitwise=True
        )

    def arith(self):
        return self.binary_operator(self.term, (TOKENS['ADD'], TOKENS['SUB']))

    def term(self):
        return self.binary_operator(
            self.factor,
            (TOKENS['MUL'], TOKENS['DIV'], TOKENS['FDIV'], TOKENS['MOD'], TOKENS['AT'])
        )

    def factor(self):
        result = PysParserResult()
        token = self.current_token

        if token.type in (TOKENS['ADD'], TOKENS['SUB'], TOKENS['NOT']):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = result.register(self.factor(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node,
                    operand_position=NUNR_LEFT
                )
            )

        return self.power()

    def power(self):
        result = PysParserResult()

        left = result.register(self.incremental())
        if result.error:
            return result

        reverse_pow_xor = self.flags & REVERSE_POW_XOR

        if self.current_token.type == (TOKENS['XOR'] if reverse_pow_xor else TOKENS['POW']):
            operand = (
                PysToken(
                    TOKENS['POW'],
                    self.current_token.position,
                    'reversed'
                )
                if reverse_pow_xor else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            right = result.register(self.factor(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def incremental(self):
        result = PysParserResult()
        token = self.current_token

        if token.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = result.register(self.primary())
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node,
                    operand_position=NUNR_LEFT
                )
            )

        node = result.register(self.primary())
        if result.error:
            return result

        if self.current_token.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = PysUnaryOperatorNode(
                operand,
                node,
                operand_position=NUNR_RIGHT
            )

        return result.success(node)

    def primary(self):
        result = PysParserResult()
        start = self.current_token.position.start

        node = result.register(self.atom())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['LPAREN'],
            TOKENS['LSQUARE'],
            TOKENS['DOT']
        ):

            if self.current_token.type == TOKENS['LPAREN']:
                left_parenthesis_token = self.current_token

                self.parenthesis_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

                seen_keyword_argument = False
                arguments = []

                while self.current_token.type not in PARENTHESISES_MAP.values():

                    argument_or_keyword = result.register(self.single_expr(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['EQ']:
                        if not isinstance(argument_or_keyword, PysIdentifierNode):
                            return result.failure(
                                self.error("expected identifier (before '=')", argument_or_keyword.position)
                            )

                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        seen_keyword_argument = True

                    elif seen_keyword_argument:
                        return result.failure(self.error("expected '=' (follows keyword argument)"))

                    if seen_keyword_argument:
                        value = result.register(self.single_expr(), True)
                        if result.error:
                            return result

                        arguments.append((argument_or_keyword.token, value))

                    else:
                        arguments.append(argument_or_keyword)

                    self.skip(result)

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                    elif self.current_token.type not in PARENTHESISES_MAP.values():
                        return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end

                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.parenthesis_level -= 1

                self.skip_expr(result)

                node = PysCallNode(node, arguments, PysPosition(self.tokens[0].position.file, start, end))
                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['LSQUARE']:
                left_parenthesis_token = self.current_token

                self.parenthesis_level += 1

                slices = []
                single_slice = True
                indices = [None, None, None]
                index = 1

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    indices[0] = result.register(self.single_expr(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        single_slice = False

                if not single_slice or self.current_token.type in PARENTHESISES_MAP.values():
                    slices.append(indices[0])
                    index -= 1

                while self.current_token.type not in PARENTHESISES_MAP.values():

                    if self.current_token.type != TOKENS['COLON']:
                        indices[index] = result.register(self.single_expr(), True)
                        if result.error:
                            return result

                        index += 1

                    single_index = self.current_token.type != TOKENS['COLON']

                    while index < 3 and self.current_token.type == TOKENS['COLON']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        if self.current_token.type in PARENTHESISES_MAP.values():
                            break

                        indices[index] = result.try_register(self.single_expr())
                        if result.error:
                            return result

                        self.skip(result)
                        index += 1

                    if single_index:
                        slices.append(indices[0])
                    else:
                        slices.append(slice(indices[0], indices[1], indices[2]))

                    indices = [None, None, None]
                    index = 0

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        single_slice = False

                    elif self.current_token.type not in PARENTHESISES_MAP.values():
                        return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end

                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.parenthesis_level -= 1

                self.skip_expr(result)

                if single_slice:
                    slices = slices[0]

                node = PysSubscriptNode(node, slices, PysPosition(self.tokens[0].position.file, start, end))
                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['DOT']:
                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                attribute = self.current_token
                start = self.current_token.position.start

                if attribute.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                node = PysAttributeNode(node, attribute)

        return result.success(node)

    def atom(self):
        result = PysParserResult()
        token = self.current_token

        if token.matches(TOKENS['KEYWORD'], (KEYWORDS['__debug__'],
                                             KEYWORDS['True'], KEYWORDS['False'], KEYWORDS['None'],
                                             KEYWORDS['true'], KEYWORDS['false'], KEYWORDS['none'])):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysKeywordNode(token))

        elif token.type == TOKENS['IDENTIFIER']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysIdentifierNode(token))

        elif token.type == TOKENS['NUMBER']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysNumberNode(token))

        elif token.type == TOKENS['STRING']:
            format = type(token.value)
            string = '' if format is str else b''

            while self.current_token.type == TOKENS['STRING']:

                if not isinstance(self.current_token.value, format):
                    return result.failure(
                        self.error(
                            "cannot mix bytes and nonbytes literals",
                            self.current_token.position
                        )
                    )

                string += self.current_token.value

                end = self.current_token.position.end

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

            return result.success(
                PysStringNode(
                    PysToken(
                        TOKENS['STRING'],
                        PysPosition(self.tokens[0].position.file, token.position.start, end),
                        string
                    )
                )
            )

        elif token.type == TOKENS['LPAREN']:
            return self.sequence_expr(NSEQ_TUPLE)

        elif token.type == TOKENS['LSQUARE']:
            return self.sequence_expr(NSEQ_LIST)

        elif token.type == TOKENS['LBRACE']:
            dict_expr = result.try_register(self.sequence_expr(NSEQ_DICT))
            if result.error:
                return result

            if not dict_expr:
                self.reverse(result.to_reverse_count)
                return self.sequence_expr(NSEQ_SET)

            return result.success(dict_expr)

        elif token.type == TOKENS['ELLIPSIS']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysEllipsisNode(token.position))

        return result.failure(self.error("expected expression"), fatal=False)

    def sequence_expr(self, type, should_sequence=False):
        result = PysParserResult()
        start = self.current_token.position.start

        elements = []

        left_parenthesis = PARENTHESISES_ITERABLE_MAP[type]

        if self.current_token.type != left_parenthesis:
            return result.failure(self.error(f"expected {chr(left_parenthesis)!r}"))

        left_parenthesis_token = self.current_token

        self.parenthesis_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        if type == NSEQ_DICT:
            always_dict = False

            while self.current_token.type not in PARENTHESISES_MAP.values():

                key = result.register(self.single_expr(), True)
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    if not always_dict:
                        self.parenthesis_level -= 1

                    return result.failure(self.error("expected ':'"), fatal=always_dict)

                result.register_advancement()
                self.advance()
                self.skip(result)

                value = result.register(self.single_expr(), True)
                if result.error:
                    return result

                elements.append((key, value))

                always_dict = True

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                elif self.current_token.type not in PARENTHESISES_MAP.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        else:

            while self.current_token.type not in PARENTHESISES_MAP.values():

                elements.append(result.register(self.single_expr(), True))
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    should_sequence = True

                elif self.current_token.type not in PARENTHESISES_MAP.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        self.parenthesis_level -= 1

        self.skip_expr(result)

        if type == NSEQ_TUPLE and not should_sequence and elements:
            return result.success(elements[0])

        return result.success(
            PysSequenceNode(
                type,
                elements,
                PysPosition(
                    self.tokens[0].position.file,
                    start,
                    end
                )
            )
        )

    def assign_expr(self):
        result = PysParserResult()

        node = result.register(self.expr())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['EQ'],
            TOKENS['EADD'],
            TOKENS['ESUB'],
            TOKENS['EMUL'],
            TOKENS['EDIV'],
            TOKENS['EFDIV'],
            TOKENS['EMOD'],
            TOKENS['EAT'],
            TOKENS['EPOW'],
            TOKENS['EAND'],
            TOKENS['EOR'],
            TOKENS['EXOR'],
            TOKENS['ELSHIFT'],
            TOKENS['ERSHIFT']
        ):
            operand = (
                PysToken(
                    TOKENS['EPOW']
                    if self.current_token.type == TOKENS['EXOR'] else
                    TOKENS['EXOR'],
                    self.current_token.position,
                    'reversed'
                )
                if 
                    self.flags & REVERSE_POW_XOR and
                    self.current_token.type in (TOKENS['EPOW'], TOKENS['EXOR'])
                else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            value = result.register(self.assign_expr(), True)
            if result.error:
                return result

            node = PysAssignNode(node, operand, value)

        return result.success(node)

    def from_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['from']):
            return result.failure(self.error(f"expected {KEYWORDS['from']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.error("expected string or identifier"))

        name = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return result.failure(self.error(f"expected {KEYWORDS['import']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['MUL']:
            result.register_advancement()
            self.advance()

            packages = NIMP_ALL

        else:
            packages = []

            if self.current_token.type in PARENTHESISES_MAP.keys():
                parenthesis = True
                left_parenthesis_token = self.current_token

                self.parenthesis_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

            else:
                parenthesis = False

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

            while self.current_token.type == TOKENS['IDENTIFIER']:
                package = self.current_token

                if name.value == '__future__':
                    processed = result.register(self.proccess_future(package.value))
                    if result.error:
                        return result
                else:
                    processed = False

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
                    result.register_advancement()
                    self.advance()
                    self.skip_expr(result)

                    if self.current_token.type != TOKENS['IDENTIFIER']:
                        return result.failure(self.error("expected identifier"))

                    as_package = self.current_token

                    result.register_advancement()
                    self.advance()
                    self.skip_expr(result)

                else:
                    as_package = None

                if not processed:
                    packages.append((package, as_package))

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip_expr(result)

                elif parenthesis and self.current_token.type not in PARENTHESISES_MAP.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                else:
                    break

            if parenthesis:
                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.parenthesis_level -= 1

        return result.success(
            PysImportNode(
                (name, None),
                packages,
                position
            )
        )

    def import_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return result.failure(self.error(f"expected {KEYWORDS['import']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.error("expected string or identifier"))

        name = self.current_token

        result.register_advancement()
        self.advance()

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

            as_name = self.current_token

            result.register_advancement()
            self.advance()

        else:
            as_name = None
            self.reverse(advance_count)

        return result.success(
            PysImportNode(
                (name, as_name),
                [],
                position
            )
        )

    def if_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        cases = result.register(self.if_expr_cases(KEYWORDS['if']))
        if result.error:
            return result

        return result.success(
            PysIfNode(
                cases[0],
                cases[1],
                position
            )
        )

    def if_expr_cases(self, case_keyword):
        result = PysParserResult()
        cases, else_body = [], None

        if not self.current_token.match(TOKENS['KEYWORD'], case_keyword):
            return result.failure(self.error(f"expected {case_keyword!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.single_expr(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        cases.append((condition, body))

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['elif']):
            all_cases = result.register(self.if_expr_cases(KEYWORDS['elif']))
            if result.error:
                return result

            new_cases, else_body = all_cases
            cases.extend(new_cases)

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['if']):
                all_cases = result.register(self.if_expr_cases(KEYWORDS['if']))
                if result.error:
                    return result

                new_cases, else_body = all_cases
                cases.extend(new_cases)

            else:
                else_body = result.register(self.block_statements(), True)
                if result.error:
                    return result

        else:
            self.reverse(advance_count)

        return result.success((cases, else_body))

    def switch_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['switch']):
            return result.failure(self.error(f"expected {KEYWORDS['switch']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.single_expr(), True)
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.error("expected '{'"))

        left_parenthesis_token = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        cases = result.register(self.case_or_default_expr())
        if result.error:
            return result

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        return result.success(
            PysSwitchNode(
                target,
                cases[0],
                cases[1],
                position
            )
        )

    def case_or_default_expr(self):
        result = PysParserResult()
        cases, default_body = [], None

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['case']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            case = result.register(self.single_expr(), True)
            if result.error:
                return result

            self.skip(result)

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.error("expected ':'"))

            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error:
                return result

            cases.append((case, body))

            self.skip(result)

            if self.current_token.matches(TOKENS['KEYWORD'], (KEYWORDS['case'], KEYWORDS['default'])):
                all_cases = result.register(self.case_or_default_expr())
                if result.error:
                    return result

                new_cases, default_body = all_cases
                cases.extend(new_cases)

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['default']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.error("expected ':'"))

            result.register_advancement()
            self.advance()

            default_body = result.register(self.statements())
            if result.error:
                return result

        return result.success((cases, default_body))

    def try_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['try']):
            return result.failure(self.error(f"expected {KEYWORDS['try']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        catch_cases = []

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['catch']):
            all_catch_handler = False

            while self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['catch']):

                if all_catch_handler:
                    return result.failure(self.error("only one catch-all except clause allowed"))

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == TOKENS['LPAREN']:
                    parenthesis = True
                    left_parenthesis_token = self.current_token

                    self.parenthesis_level += 1

                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    if self.current_token.type != TOKENS['IDENTIFIER']:
                        return result.failure(self.error("expected identifier"))

                else:
                    parenthesis = False

                if self.current_token.type == TOKENS['IDENTIFIER']:
                    parameter = self.current_token

                    result.register_advancement()
                    self.advance()
                    self.skip_expr(result)

                    if (
                        self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']) or
                        self.current_token.type == TOKENS['COMMA']
                    ):
                        result.register_advancement()
                        self.advance()
                        self.skip_expr(result)

                        if self.current_token.type != TOKENS['IDENTIFIER']:
                            return result.failure(self.error("expected identifier"))

                    if self.current_token.type == TOKENS['IDENTIFIER']:
                        target = PysIdentifierNode(parameter)
                        parameter = self.current_token

                        result.register_advancement()
                        self.advance()
                        self.skip_expr(result)

                    else:
                        target = None
                        all_catch_handler = True

                    catch_parameter = (target, parameter)

                else:
                    catch_parameter = (None, None)
                    all_catch_handler = True

                if parenthesis:
                    self.close_parenthesis(result, left_parenthesis_token)
                    if result.error:
                        return result

                    self.parenthesis_level -= 1

                self.skip(result)

                catch_body = result.register(self.block_statements(), True)
                if result.error:
                    return result

                catch_cases.append((catch_parameter, catch_body))

                advance_count = self.skip(result)

            if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
                result.register_advancement()
                self.advance()
                self.skip(result)

                else_body = result.register(self.block_statements(), True)
                if result.error:
                    return result

                advance_count = self.skip(result)

            else:
                else_body = None

        else:
            else_body = None

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['finally']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            finally_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        elif not catch_cases:
            return result.failure(self.error(f"expected {KEYWORDS['catch']!r} or {KEYWORDS['finally']!r}"))

        else:
            finally_body = None
            self.reverse(advance_count)

        return result.success(
            PysTryNode(
                body,
                catch_cases,
                else_body,
                finally_body,
                position
            )
        )

    def with_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['with']):
            return result.failure(self.error(f"expected {KEYWORDS['with']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LPAREN']:
            parenthesis = True
            left_parenthesis_token = self.current_token

            self.parenthesis_level += 1

            result.register_advancement()
            self.advance()
            self.skip(result)

        else:
            parenthesis = False

        context = result.register(self.single_expr(), True)
        if result.error:
            return result

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

        if self.current_token.type == TOKENS['IDENTIFIER']:
            alias = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

        else:
            alias = None

        if parenthesis:
            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

            self.parenthesis_level -= 1

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        return result.success(
            PysWithNode(
                context,
                alias,
                body,
                position
            )
        )

    def for_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['for']):
            return result.failure(self.error(f"expected {KEYWORDS['for']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LPAREN']:
            parenthesis = True
            left_parenthesis_token = self.current_token

            self.parenthesis_level += 1

            result.register_advancement()
            self.advance()
            self.skip(result)

        else:
            parenthesis = False

        declaration = result.try_register(self.assign_expr())
        if result.error:
            return result

        if self.current_token.type == TOKENS['SEMICOLON']:
            iteration = False

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            condition = result.try_register(self.single_expr())
            if result.error:
                return result

            if self.current_token.type != TOKENS['SEMICOLON']:
                return result.failure(self.error("expected ';'"))

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            update = result.try_register(self.assign_expr())
            if result.error:
                return result

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['of']):
            if declaration is None:
                return result.failure(
                    self.error(f"expected assign expression. Did you mean ';' instead of {KEYWORDS['of']!r}?")
                )

            iteration = True

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            iterable = result.register(self.single_expr(), True)
            if result.error:
                return result

        elif declaration is None:
            return result.failure(self.error("expected assign expression or ';'"))

        else:
            return result.failure(self.error(f"expected {KEYWORDS['of']!r} or ';'"))

        if parenthesis:
            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

            self.parenthesis_level -= 1

        self.skip(result)

        body = result.try_register(self.block_statements())
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(
            PysForNode(
                (declaration, iterable) if iteration else (declaration, condition, update),
                body,
                else_body,
                position
            )
        )

    def while_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return result.failure(self.error(f"expected {KEYWORDS['while']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.single_expr(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.try_register(self.block_statements())
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(
            PysWhileNode(
                condition,
                body,
                else_body,
                position
            )
        )

    def do_while_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['do']):
            return result.failure(self.error(f"expected {KEYWORDS['do']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.try_register(self.block_statements())
        if result.error:
            return result

        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return result.failure(self.error(f"expected {KEYWORDS['while']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.single_expr(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(
            PysDoWhileNode(
                body,
                condition,
                else_body,
                position
            )
        )

    def class_expr(self, decorators=None):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
            return result.failure(self.error(f"expected {KEYWORDS['class']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['IDENTIFIER']:
            return result.failure(self.error("expected identifier"))

        name = self.current_token
        end = self.current_token.position.end

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LPAREN']:
            bases = result.register(self.sequence_expr(NSEQ_TUPLE, should_sequence=True))
            if result.error:
                return result

            end = bases.position.end
            bases = list(bases.elements)

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['extends']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            bases = result.register(self.expr(), True)
            if result.error:
                return result

            end = bases.position.end

            if isinstance(bases, PysSequenceNode):
                bases = list(bases.elements)
                if not bases:
                    return result.failure(self.error("empty base not allowed", bases.position))

            else:
                bases = [bases]

        else:
            bases = []

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        return result.success(
            PysClassNode(
                [] if decorators is None else decorators,
                name,
                bases,
                body,
                PysPosition(
                    self.tokens[0].position.file,
                    start,
                    end
                )
            )
        )

    def func_expr(self, decorators=None):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
            return result.failure(self.error(f"expected {KEYWORDS['func']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['IDENTIFIER']:
            name = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

        else:
            name = None

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.error("expected identifier or '('" if name is None else "expected '('"))

        left_parenthesis_token = self.current_token

        self.parenthesis_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        seen_keyword_argument = False
        parameters = []

        while self.current_token.type not in PARENTHESISES_MAP.values():

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

            key = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['EQ']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                seen_keyword_argument = True

            elif seen_keyword_argument:
                return result.failure(self.error("expected '=' (follows keyword argument)"))

            if seen_keyword_argument:
                value = result.register(self.single_expr(), True)
                if result.error:
                    return result

                parameters.append((key, value))

            else:
                parameters.append(key)

            self.skip(result)

            if self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

            elif self.current_token.type not in PARENTHESISES_MAP.values():
                return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        self.parenthesis_level -= 1

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        return result.success(
            PysFunctionNode(
                [] if decorators is None else decorators,
                name,
                parameters,
                body,
                PysPosition(self.tokens[0].position.file, start, end)
            )
        )

    def return_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['return']):
            return result.failure(self.error(f"expected {KEYWORDS['return']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        value = result.try_register(self.expr())
        if result.error:
            return result

        if not value:
            self.reverse(result.to_reverse_count)

        return result.success(
            PysReturnNode(
                value,
                position
            )
        )

    def global_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['global']):
            return result.failure(self.error(f"expected {KEYWORDS['global']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        names = []

        if self.current_token.type in PARENTHESISES_MAP.keys():
            left_parenthesis_token = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            while self.current_token.type not in PARENTHESISES_MAP.values():

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                names.append(self.current_token)

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                elif self.current_token.type not in PARENTHESISES_MAP.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

            if not names:
                return result.failure(self.error("invalid syntax. At least need 1 identifier"))

            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

        elif self.current_token.type == TOKENS['IDENTIFIER']:
            names.append(self.current_token)

            result.register_advancement()
            self.advance()

        else:
            return result.failure(self.error("expected identifier, '[', '(', or '{'"))

        return result.success(
            PysSequenceNode(
                NSEQ_GLOBAL,
                names,
                position
            )
        )

    def del_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['del']):
            return result.failure(self.error(f"expected {KEYWORDS['del']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.expr(), True)
        if result.error:
            return result

        if isinstance(expr, PysSequenceNode):
            targets = list(expr.elements)
            if not targets:
                return result.failure(self.error("empty target not allowed", expr.position))

        else:
            targets = [expr]

        return result.success(
            PysSequenceNode(
                NSEQ_DEL,
                targets,
                position
            )
        )

    def throw_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['throw']):
            return result.failure(self.error(f"expected {KEYWORDS['throw']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.single_expr(), True)
        if result.error:
            return result

        return result.success(
            PysThrowNode(
                target,
                position
            )
        )

    def assert_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['assert']):
            return result.failure(self.error(f"expected {KEYWORDS['assert']!r}"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.single_expr(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.type == TOKENS['COMMA']:
            result.register_advancement()
            self.advance()
            self.skip(result)

            message = result.register(self.single_expr(), True)
            if result.error:
                return result

        else:
            message = None
            self.reverse(advance_count)

        return result.success(
            PysAssertNode(
                condition,
                message
            )
        )

    def decorator_expr(self):
        result = PysParserResult()

        if self.current_token.type != TOKENS['AT']:
            return result.failure(self.error("expected '@'"))

        decorators = []

        while self.current_token.type == TOKENS['AT']:
            result.register_advancement()
            self.advance()

            decorators.append(result.register(self.single_expr(), True))
            if result.error:
                return result

            self.skip(result, (TOKENS['NEWLINE'], TOKENS['SEMICOLON']))

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
            func_expr = result.register(self.func_expr(decorators))
            if result.error:
                return result

            return result.success(func_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
            class_expr = result.register(self.class_expr(decorators))
            if result.error:
                return result

            return result.success(class_expr)

        return result.failure(self.error("expected function or class declaration after decorator"))

    def block_statements(self):
        result = PysParserResult()

        if self.current_token.type == TOKENS['LBRACE']:
            left_parenthesis_token = self.current_token

            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error:
                return result

            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

            return result.success(body)

        elif self.current_token.type == TOKENS['COLON']:
            return result.failure(self.error("unlike python"))

        body = result.register(self.statement())
        if result.error:
            return result.failure(self.error("expected statement, expression, or '{'"), fatal=False)

        return result.success(body)

    def chain_operator(self, func, operators, is_member=False):
        result = PysParserResult()

        operations = []
        expressions = []

        expr = result.register(func())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operations.append(self.current_token)
            expressions.append(expr)

            if is_member and self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['not']):
                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['in']):
                    return result.failure(self.error(f"expected {KEYWORDS['in']!r}"))

                operations[-1] = PysToken(
                    TOKENS['NOTIN'],
                    self.current_token.position,
                    f"{KEYWORDS['not']} {KEYWORDS['in']}"
                )

            last_token = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            if (
                is_member and
                last_token.match(TOKENS['KEYWORD'], KEYWORDS['is']) and
                self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['not'])
            ):
                operations[-1] = PysToken(
                    TOKENS['ISNOT'],
                    self.current_token.position,
                    f"{KEYWORDS['is']} {KEYWORDS['not']}"
                )

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

            expr = result.register(func(), True)
            if result.error:
                return result

        if operations:
            expressions.append(expr)

        return result.success(
            PysChainOperatorNode(
                operations,
                expressions
            )
            if operations else
            expr
        )

    def binary_operator(self, func, operators, is_bitwise=False):
        result = PysParserResult()

        left = result.register(func())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operand = (
                PysToken(
                    TOKENS['XOR'],
                    self.current_token.position,
                    'reversed'
                )
                if
                    is_bitwise and
                    self.flags & REVERSE_POW_XOR and
                    self.current_token.type == TOKENS['POW']
                else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            right = result.register(func(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def close_parenthesis(self, result, left_parenthesis_token):
        if self.current_token.type != PARENTHESISES_MAP[left_parenthesis_token.type]:

            if self.current_token.type in PARENTHESISES_MAP.values():
                return result.failure(
                    self.error(
                        "closing parenthesis " + 
                        repr(chr(self.current_token.type)) +
                        " does not match opening parenthesis " +
                        repr(chr(left_parenthesis_token.type))
                    )
                )

            elif self.current_token.type == TOKENS['EOF']:
                return result.failure(
                    self.error(
                        f"{chr(left_parenthesis_token.type)!r} was never closed",
                        left_parenthesis_token.position
                    )
                )

            else:
                return result.failure(self.error("invalid syntax"))

        result.register_advancement()
        self.advance()

    def skip(self, result, types=TOKENS['NEWLINE']):
        if not isinstance(types, tuple):
            types = (types,)

        count = 0

        while self.current_token.type in types:
            result.register_advancement()
            self.advance()
            count += 1

        return count

    def skip_expr(self, result):
        if self.parenthesis_level > 0:
            return self.skip(result)

        return 0

    def proccess_future(self, name):
        result = PysParserResult()

        if name == 'braces':
            return result.failure(self.error("yes, i use it for this language"))

        elif name == 'indent':
            return result.failure(self.error("not a chance"))

        elif name == '__67__':
            return result.failure(
                self.error("What is this diddy blud doing on the code editor is blud Guido van Rossum?")
            )

        elif name == 'reverse_pow_xor':
            self.flags |= REVERSE_POW_XOR
            return result.success(True)

        return result.failure(self.error(f"future feature {name} is not defined"))