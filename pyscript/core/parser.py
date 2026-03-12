from .bases import Pys
from .checks import is_list, is_left_bracket, is_right_bracket
from .constants import TOKENS, DEFAULT, DICT_TO_JSDICT
from .context import PysContext
from .exceptions import PysTraceback
from .mapping import BRACKETS_MAP
from .nodes import *
from .position import PysPosition
from .results import PysParserResult
from .token import PysToken
from .utils.decorators import typechecked
from .utils.generic import setimuattr
from .utils.jsdict import jsdict

from types import MappingProxyType
from typing import Any, Callable, Optional

SEQUENCES_MAP = MappingProxyType({
    'dict': (TOKENS['LEFT_CURLY'], PysDictionaryNode),
    'set': (TOKENS['LEFT_CURLY'], PysSetNode),
    'list': (TOKENS['LEFT_SQUARE'], PysListNode),
    'tuple': (TOKENS['LEFT_PARENTHESIS'], PysTupleNode)
})

class PysParser(Pys):

    @typechecked
    def __init__(
        self,
        tokens: tuple[PysToken, ...] | tuple[PysToken],
        flags: int = DEFAULT,
        parser_flags: int = DEFAULT,
        context_parent: Optional[PysContext] = None,
        context_parent_entry_position: Optional[PysPosition] = None
    ) -> None:

        self.tokens = tokens
        self.flags = flags
        self.parser_flags = parser_flags
        self.context_parent = context_parent
        self.context_parent_entry_position = context_parent_entry_position

    @typechecked
    def parse(
        self,
        function: Optional[Callable[[], PysParserResult]] = None
    ) -> tuple[PysNode, None] | tuple[None, PysTraceback]:

        self.token_index = 0
        self.bracket_level = 0

        self.update_current_token()

        result = (function or self.statements)()

        if not result.error:
            if is_right_bracket(self.current_token.type):
                result.failure(self.new_error(f"unmatched {chr(self.current_token.type)!r}"))
            elif self.current_token.type != TOKENS['NULL']:
                result.failure(self.new_error("invalid syntax"))

        return result.node, result.error

    def update_current_token(self) -> None:
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def advance(self) -> None:
        self.token_index += 1
        self.update_current_token()

    def reverse(self, amount: int = 1) -> None:
        self.token_index -= amount
        self.update_current_token()

    def new_error(self, message: str, position: Optional[PysPosition] = None) -> PysTraceback:
        return PysTraceback(
            SyntaxError(message),
            PysContext(
                file=self.current_token.position.file,
                flags=self.flags,
                parent=self.context_parent,
                parent_entry_position=self.context_parent_entry_position
            ),
            position or self.current_token.position
        )

    def statements(self) -> PysParserResult:
        result = PysParserResult()
        start = self.current_token.position.start

        statements = []
        more_statements = True
        bracket_level = self.bracket_level

        self.bracket_level = 0

        while True:
            advance_count = self.skip(result, TOKENS['NEWLINE'], TOKENS['SEMICOLON'])

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

        self.bracket_level = bracket_level

        return result.success(
            PysStatementsNode(
                statements,
                PysPosition(
                    self.current_token.position.file,
                    start,
                    self.current_token.position.end
                )
            )
        )

    def statement(self) -> PysParserResult:
        if self.current_token.match(TOKENS['KEYWORD'], 'from'):
            return self.from_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'import'):
            return self.import_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'if'):
            return self.if_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'switch'):
            return self.switch_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'try'):
            return self.try_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'with'):
            return self.with_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'for'):
            return self.for_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'while'):
            return self.while_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'do'):
            return self.do_while_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'repeat'):
            return self.repeat_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'class'):
            return self.class_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'return'):
            return self.return_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'global'):
            return self.global_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'del', 'delete'):
            return self.del_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'raise', 'throw'):
            return self.throw_statement()

        elif self.current_token.match(TOKENS['KEYWORD'], 'assert'):
            return self.assert_statement()

        elif self.current_token.type == TOKENS['AT']:
            return self.decorator()

        elif self.current_token.match(TOKENS['KEYWORD'], 'continue'):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysContinueNode(position))

        elif self.current_token.match(TOKENS['KEYWORD'], 'break'):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysBreakNode(position))

        result = PysParserResult()

        assignment_expression = result.register(self.assignment_statement())
        if result.error:
            return result.failure(self.new_error("expected an expression or statement"), fatal=False)

        return result.success(assignment_expression)

    def expression(self, function: Optional[Callable[[], PysParserResult]] = None) -> PysParserResult:
        function = function or self.single_expression
        result = PysParserResult()

        node = result.register(function())
        if result.error:
            return result

        if self.current_token.type == TOKENS['COMMA']:
            elements = [node]

            while self.current_token.type == TOKENS['COMMA']:
                end = self.current_token.position.end
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                element = result.try_register(function())
                if result.error:
                    return result

                if element:
                    end = element.position.end
                    elements.append(element)
                else:
                    self.reverse(result.to_reverse_count)
                    break

            self.skip_expression(result)

            node = PysTupleNode(
                elements,
                PysPosition(
                    self.current_token.position.file,
                    node.position.start,
                    end
                )
            )

        return result.success(node)

    def walrus(self) -> PysParserResult:
        result = PysParserResult()

        node = result.register(self.single_expression())
        if result.error:
            return result

        if self.current_token.type == TOKENS['EQUAL_COLON']:
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            value = result.register(self.single_expression(), True)
            if result.error:
                return result

            node = PysAssignmentNode(node, operand, value)

        return result.success(node)

    def single_expression(self) -> PysParserResult:
        if self.current_token.match(TOKENS['KEYWORD'], 'match'):
            return self.match_expression()

        elif self.current_token.match(TOKENS['KEYWORD'], 'def', 'define', 'func', 'function', 'constructor'):
            return self.func_expression()

        elif self.current_token.match(TOKENS['KEYWORD'], 'typeof'):
            operand = self.current_token
            result = PysParserResult()

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            node = result.register(self.single_expression(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    operand,
                    node
                )
            )

        return self.ternary()

    def ternary(self) -> PysParserResult:
        result = PysParserResult()

        node = result.register(self.nullish())
        if result.error:
            return result

        if self.current_token.type == TOKENS['QUESTION']:
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            valid = result.register(self.ternary(), True)
            if result.error:
                return result

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.new_error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            invalid = result.register(self.ternary(), True)
            if result.error:
                return result

            node = PysTernaryOperatorNode(
                node,
                valid,
                invalid,
                style='general'
            )

        elif self.current_token.match(TOKENS['KEYWORD'], 'if'):
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            condition = result.register(self.ternary(), True)
            if result.error:
                return result

            if not self.current_token.match(TOKENS['KEYWORD'], 'else'):
                return result.failure(self.new_error("expected 'else'"))

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            invalid = result.register(self.ternary(), True)
            if result.error:
                return result

            node = PysTernaryOperatorNode(
                condition,
                node,
                invalid,
                style='pythonic'
            )

        return result.success(node)

    def nullish(self) -> PysParserResult:
        return self.binary_operator(self.logic, TOKENS['DOUBLE_QUESTION'])

    def logic(self) -> PysParserResult:
        return self.binary_operator(
            self.member,
            (TOKENS['KEYWORD'], 'and'),
            (TOKENS['KEYWORD'], 'or'),
            TOKENS['DOUBLE_AMPERSAND'], TOKENS['DOUBLE_PIPE']
        )

    def member(self) -> PysParserResult:
        return self.chain_operator(
            self.comparison,
            (TOKENS['KEYWORD'], 'in'),
            (TOKENS['KEYWORD'], 'is'),
            (TOKENS['KEYWORD'], 'not'),
            TOKENS['MINUS_GREATER_THAN'], TOKENS['EXCLAMATION_GREATER_THAN'],
            membership=True
        )

    def comparison(self) -> PysParserResult:
        token = self.current_token

        if token.match(TOKENS['KEYWORD'], 'not') or token.type == TOKENS['EXCLAMATION']:
            result = PysParserResult()

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            node = result.register(self.comparison(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node
                )
            )

        return self.chain_operator(
            self.bitwise,
            TOKENS['DOUBLE_EQUAL'], TOKENS['EQUAL_EXCLAMATION'], TOKENS['EQUAL_TILDE'], TOKENS['EXCLAMATION_TILDE'],
            TOKENS['LESS_THAN'], TOKENS['GREATER_THAN'], TOKENS['EQUAL_LESS_THAN'], TOKENS['EQUAL_GREATER_THAN']
        )

    def bitwise(self) -> PysParserResult:
        return self.binary_operator(
            self.arithmetic,
            TOKENS['AMPERSAND'], TOKENS['PIPE'], TOKENS['CIRCUMFLEX'], TOKENS['DOUBLE_LESS_THAN'],
            TOKENS['DOUBLE_GREATER_THAN']
        )

    def arithmetic(self) -> PysParserResult:
        return self.binary_operator(self.term, TOKENS['PLUS'], TOKENS['MINUS'])

    def term(self) -> PysParserResult:
        return self.binary_operator(
            self.factor,
            TOKENS['STAR'], TOKENS['SLASH'], TOKENS['DOUBLE_SLASH'], TOKENS['PERCENT'], TOKENS['AT']
        )

    def factor(self) -> PysParserResult:
        token = self.current_token

        if token.type in (TOKENS['PLUS'], TOKENS['MINUS'], TOKENS['TILDE']):
            result = PysParserResult()

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            node = result.register(self.factor(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node
                )
            )

        return self.power()

    def power(self) -> PysParserResult:
        result = PysParserResult()

        left = result.register(self.incremental())
        if result.error:
            return result

        if self.current_token.type == TOKENS['DOUBLE_STAR']:
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            right = result.register(self.factor(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def incremental(self) -> PysParserResult:
        result = PysParserResult()
        token = self.current_token

        if token.type in (TOKENS['DOUBLE_PLUS'], TOKENS['DOUBLE_MINUS']):
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            node = result.register(self.primary())
            if result.error:
                return result

            return result.success(
                PysIncrementalNode(
                    token,
                    node,
                    operand_position='left'
                )
            )

        node = result.register(self.primary())
        if result.error:
            return result

        if self.current_token.type in (TOKENS['DOUBLE_PLUS'], TOKENS['DOUBLE_MINUS']):
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            node = PysIncrementalNode(
                operand,
                node,
                operand_position='right'
            )

        return result.success(node)

    def primary(self) -> PysParserResult:
        result = PysParserResult()
        start = self.current_token.position.start

        node = result.register(self.atom())
        if result.error:
            return result

        while True:

            if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
                left_bracket_token = self.current_token
                self.bracket_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

                seen_keyword_argument = False
                arguments = []

                while not is_right_bracket(self.current_token.type):

                    argument_or_keyword = result.register(self.walrus(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['EQUAL']:
                        if not isinstance(argument_or_keyword, PysIdentifierNode):
                            return result.failure(
                                self.new_error("expected identifier (before '=')", argument_or_keyword.position)
                            )

                        result.register_advancement()
                        self.advance()
                        self.skip(result)
                        seen_keyword_argument = True

                    elif seen_keyword_argument:
                        return result.failure(self.new_error("expected '=' (follows keyword argument)"))

                    if seen_keyword_argument:
                        value = result.register(self.single_expression(), True)
                        if result.error:
                            return result
                        arguments.append((argument_or_keyword.name, value))
                    else:
                        arguments.append(argument_or_keyword)

                    self.skip(result)

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                    elif self.current_token.type == TOKENS['NULL']:
                        break

                    elif not is_right_bracket(self.current_token.type):
                        return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end
                self.close_bracket(result, left_bracket_token)
                if result.error:
                    return result

                self.bracket_level -= 1
                self.skip_expression(result)

                node = PysCallNode(
                    node,
                    arguments,
                    PysPosition(
                        self.current_token.position.file,
                        start,
                        end
                    )
                )

            elif self.current_token.type == TOKENS['LEFT_SQUARE']:
                left_bracket_token = self.current_token
                self.bracket_level += 1

                index = 0
                slices = []
                indices = [None, None, None]
                single_slice = True

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    indices[0] = result.register(self.walrus(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)
                        single_slice = False

                if not single_slice or is_right_bracket(self.current_token.type):
                    slices.append(indices[0])
                    indices = [None, None, None]

                while not is_right_bracket(self.current_token.type):

                    if self.current_token.type != TOKENS['COLON']:
                        indices[index] = result.register(self.walrus(), True)
                        if result.error:
                            return result

                    index += 1
                    single_index = self.current_token.type != TOKENS['COLON']

                    while index < 3 and self.current_token.type == TOKENS['COLON']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        if is_right_bracket(self.current_token.type):
                            break

                        indices[index] = result.try_register(self.walrus())
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

                    elif self.current_token.type == TOKENS['NULL']:
                        break

                    elif not is_right_bracket(self.current_token.type):
                        return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end
                self.close_bracket(result, left_bracket_token)
                if result.error:
                    return result

                self.bracket_level -= 1
                self.skip_expression(result)

                if single_slice:
                    slices = slices[0]

                node = PysSubscriptNode(
                    node,
                    slices,
                    PysPosition(
                        self.current_token.position.file,
                        start,
                        end
                    )
                )

            elif self.current_token.type == TOKENS['DOT']:
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                attribute = self.current_token

                if attribute.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.new_error("expected identifier"))

                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                node = PysAttributeNode(node, attribute)

            else:
                break

        return result.success(node)

    def atom(self) -> PysParserResult:
        result = PysParserResult()
        token = self.current_token

        if token.match(TOKENS['KEYWORD'], '__debug__', 'True', 'False', 'None', 'true', 'false', 'nil', 'none', 'null'):
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            return result.success(PysKeywordNode(token))

        elif token.type == TOKENS['IDENTIFIER']:
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            return result.success(PysIdentifierNode(token))

        elif token.type == TOKENS['NUMBER']:
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            return result.success(PysNumberNode(token))

        elif token.type == TOKENS['STRING']:
            format = type(token.value)
            string = '' if format is str else b''

            while self.current_token.type == TOKENS['STRING']:

                if not isinstance(self.current_token.value, format):
                    return result.failure(
                        self.new_error(
                            "cannot mix bytes and nonbytes literals",
                            self.current_token.position
                        )
                    )

                string += self.current_token.value
                end = self.current_token.position.end

                result.register_advancement()
                self.advance()
                self.skip_expression(result)

            return result.success(
                PysStringNode(
                    PysToken(
                        TOKENS['STRING'],
                        PysPosition(
                            self.current_token.position.file,
                            token.position.start,
                            end
                        ),
                        string
                    )
                )
            )

        elif token.type == TOKENS['LEFT_PARENTHESIS']:
            return self.sequence_expression('tuple')

        elif token.type == TOKENS['LEFT_SQUARE']:
            return self.sequence_expression('list')

        elif token.type == TOKENS['LEFT_CURLY']:
            dict_expression = result.try_register(self.sequence_expression('dict'))
            if result.error:
                return result

            if not dict_expression:
                self.reverse(result.to_reverse_count)
                return self.sequence_expression('set')

            return result.success(dict_expression)

        elif token.type == TOKENS['TRIPLE_DOT']:
            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            return result.success(PysEllipsisNode(token.position))

        return result.failure(self.new_error("expected expression"), fatal=False)

    def sequence_expression(
        self,
        type: Literal['dict', 'set', 'list', 'tuple'],
        should_sequence: bool = False
    ) -> PysParserResult:
        result = PysParserResult()
        start = self.current_token.position.start
        left_bracket, node = SEQUENCES_MAP[type]

        if self.current_token.type != left_bracket:
            return result.failure(self.new_error(f"expected {chr(left_bracket)!r}"))

        left_bracket_token = self.current_token
        self.bracket_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        elements = []

        if type == 'dict':
            dict_to_jsdict = self.parser_flags & DICT_TO_JSDICT
            always_dict = False

            while not is_right_bracket(self.current_token.type):

                if dict_to_jsdict:

                    if self.current_token.type == TOKENS['LEFT_SQUARE']:
                        left_square_token = self.current_token
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        key = result.register(self.walrus(), True)
                        if result.error:
                            return result

                        self.close_bracket(result, left_square_token)
                        if result.error:
                            return result

                    elif self.current_token.type == TOKENS['IDENTIFIER']:
                        key = PysStringNode(self.current_token)
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                    else:
                        key = result.register(self.single_expression(), True)
                        if result.error:
                            return result

                else:
                    key = result.register(self.walrus(), True)
                    if result.error:
                        return result

                if self.current_token.type not in (TOKENS['COLON'], TOKENS['EQUAL']):
                    if not always_dict:
                        self.bracket_level -= 1
                    return result.failure(self.new_error("expected ':' or '='"), fatal=always_dict)

                result.register_advancement()
                self.advance()
                self.skip(result)

                value = result.register(self.walrus(), True)
                if result.error:
                    return result

                elements.append((key, value))
                always_dict = True

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                elif self.current_token.type == TOKENS['NULL']:
                    break

                elif not is_right_bracket(self.current_token.type):
                    return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

        else:

            while not is_right_bracket(self.current_token.type):

                elements.append(result.register(self.walrus(), True))
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)
                    should_sequence = True

                elif self.current_token.type == TOKENS['NULL']:
                    break

                elif not is_right_bracket(self.current_token.type):
                    return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end
        self.close_bracket(result, left_bracket_token)
        if result.error:
            return result

        position = PysPosition(self.current_token.position.file, start, end)
        self.bracket_level -= 1
        self.skip_expression(result)

        if type == 'tuple' and not should_sequence and elements:
            element = elements[0]
            setimuattr(element, 'position', position)
            return result.success(element)

        elif type == 'dict':
            return result.success(
                node(
                    pairs=elements,
                    class_type=jsdict if dict_to_jsdict else dict,
                    position=position
                )
            )

        return result.success(node(elements, position))

    def assignment_statement(self, function: Optional[Callable[[], PysParserResult]] = None) -> PysParserResult:
        result = PysParserResult()

        node = result.register(self.expression(function))
        if result.error:
            return result

        if self.current_token.type in (
            TOKENS['EQUAL'],
            TOKENS['EQUAL_PLUS'],
            TOKENS['EQUAL_MINUS'],
            TOKENS['EQUAL_STAR'],
            TOKENS['EQUAL_SLASH'],
            TOKENS['EQUAL_DOUBLE_SLASH'],
            TOKENS['EQUAL_PERCENT'],
            TOKENS['EQUAL_AT'],
            TOKENS['EQUAL_DOUBLE_STAR'],
            TOKENS['EQUAL_AMPERSAND'],
            TOKENS['EQUAL_PIPE'],
            TOKENS['EQUAL_CIRCUMFLEX'],
            TOKENS['EQUAL_DOUBLE_LESS_THAN'],
            TOKENS['EQUAL_DOUBLE_GREATER_THAN']
        ):
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            value = result.register(self.assignment_statement(function), True)
            if result.error:
                return result

            node = PysAssignmentNode(node, operand, value)

        return result.success(node)

    def from_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'from'):
            return result.failure(self.new_error("expected 'from'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.new_error("expected string or identifier"))

        name = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], 'import'):
            return result.failure(self.new_error("expected 'import'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['STAR']:
            result.register_advancement()
            self.advance()
            packages = 'all'

        else:
            bracket = False
            packages = []

            if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
                bracket = True
                left_bracket_token = self.current_token
                self.bracket_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

            elif is_left_bracket(self.current_token.type):
                return result.failure(self.new_error(f"expected '(' not {chr(self.current_token.type)!r}"))

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.new_error("expected identifier"))

            while True:
                package = self.current_token
                as_package = None
                processed = False

                if name.value == '__future__':
                    processed = result.register(self.proccess_future(package.value))
                    if result.error:
                        return result

                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                if self.current_token.match(TOKENS['KEYWORD'], 'as'):
                    result.register_advancement()
                    self.advance()
                    self.skip_expression(result)

                    if self.current_token.type != TOKENS['IDENTIFIER']:
                        return result.failure(self.new_error("expected identifier"))

                    as_package = self.current_token

                    result.register_advancement()
                    self.advance()
                    self.skip_expression(result)

                if not processed:
                    packages.append((package, as_package))

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip_expression(result)

                elif bracket and self.current_token.type == TOKENS['NULL']:
                    break

                elif bracket and not is_right_bracket(self.current_token.type):
                    return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

                else:
                    break

            if bracket:
                self.close_bracket(result, left_bracket_token)
                if result.error:
                    return result

                self.bracket_level -= 1

        return result.success(
            PysImportNode(
                (name, None),
                packages,
                position
            )
        )

    def import_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'import'):
            return result.failure(self.new_error("expected 'import'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.new_error("expected string or identifier"))

        name = self.current_token
        as_name = None

        result.register_advancement()
        self.advance()

        if self.current_token.match(TOKENS['KEYWORD'], 'as'):
            result.register_advancement()
            self.advance()

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.new_error("expected identifier"))

            as_name = self.current_token
            result.register_advancement()
            self.advance()

        return result.success(
            PysImportNode(
                (name, as_name),
                [],
                position
            )
        )

    def if_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'if'):
            return result.failure(self.new_error("expected 'if'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.walrus(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        cases = [(condition, body)]
        else_body = None
        advance_count = self.skip(result)

        while True:

            if self.current_token.match(TOKENS['KEYWORD'], 'elif', 'elseif'):
                result.register_advancement()
                self.advance()
                self.skip(result)
                conditional_chain = True

            elif self.current_token.match(TOKENS['KEYWORD'], 'else'):
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.match(TOKENS['KEYWORD'], 'if'):
                    result.register_advancement()
                    self.advance()
                    self.skip(result)
                    conditional_chain = True

                else:
                    else_body = result.register(self.block_statements(), True)
                    if result.error:
                        return result

                    advance_count = 0
                    break

            else:
                break

            if conditional_chain:
                conditional_chain = False

                condition = result.register(self.walrus(), True)
                if result.error:
                    return result

                self.skip(result)

                body = result.register(self.block_statements(), True)
                if result.error:
                    return result

                cases.append((condition, body))
                advance_count = self.skip(result)

        self.reverse(advance_count)

        return result.success(
            PysIfNode(
                cases,
                else_body,
                position
            )
        )

    def switch_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'switch'):
            return result.failure(self.new_error("expected 'switch'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.walrus(), True)
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['LEFT_CURLY']:
            return result.failure(self.new_error("expected '{'"))

        left_bracket_token = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        cases = []
        default_body = None

        while True:

            if self.current_token.match(TOKENS['KEYWORD'], 'case'):
                result.register_advancement()
                self.advance()
                self.skip(result)

                case = result.register(self.walrus(), True)
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    return result.failure(self.new_error("expected ':'"))

                result.register_advancement()
                self.advance()

                body = result.register(self.statements())
                if result.error:
                    return result

                cases.append((case, body))

            elif self.current_token.match(TOKENS['KEYWORD'], 'default'):
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    return result.failure(self.new_error("expected ':'"))

                result.register_advancement()
                self.advance()

                default_body = result.register(self.statements())
                if result.error:
                    return result

                break

            else:
                break

        self.close_bracket(result, left_bracket_token)
        if result.error:
            return result

        return result.success(
            PysSwitchNode(
                target,
                cases,
                default_body,
                position
            )
        )

    def match_expression(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'match'):
            return result.failure(self.new_error("expected 'match'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = None

        if self.current_token.type != TOKENS['LEFT_CURLY']:
            target = result.register(self.walrus(), True)
            if result.error:
                return result.failure(self.new_error("expected expression or '{'"))

            self.skip(result)

            if self.current_token.type != TOKENS['LEFT_CURLY']:
                return result.failure(self.new_error("expected '{'"))

        left_bracket_token = self.current_token
        self.bracket_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        cases = []
        default = None

        while not is_right_bracket(self.current_token.type):

            if self.current_token.match(TOKENS['KEYWORD'], 'default'):
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    return result.failure(self.new_error("expected ':'"))

                result.register_advancement()
                self.advance()
                self.skip(result)

                default = result.register(self.single_expression(), True)
                if result.error:
                    return result

                break

            condition = result.register(self.single_expression(), True)
            if result.error:
                return result

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.new_error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            value = result.register(self.single_expression(), True)
            if result.error:
                return result

            cases.append((condition, value))

            if self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

            elif self.current_token.type == TOKENS['NULL']:
                break

            elif not is_right_bracket(self.current_token.type):
                return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

        self.close_bracket(result, left_bracket_token)
        if result.error:
            return result

        self.bracket_level -= 1
        self.skip_expression(result)

        return result.success(
            PysMatchNode(
                target,
                cases,
                default,
                position
            )
        )

    def try_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'try'):
            return result.failure(self.new_error("expected 'try'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        catch_cases = []
        else_body = None
        finally_body = None
        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'catch', 'except'):
            all_catch_handler = False

            while self.current_token.match(TOKENS['KEYWORD'], 'catch', 'except'):
                if all_catch_handler:
                    return result.failure(self.new_error("only one catch-all except clause allowed"))

                result.register_advancement()
                self.advance()
                self.skip(result)

                bracket = False
                targets = []
                parameter = None

                if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
                    bracket = True
                    left_bracket_token = self.current_token
                    self.bracket_level += 1

                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    if self.current_token.type != TOKENS['IDENTIFIER']:
                        return result.failure(self.new_error("expected identifier"))

                if self.current_token.type == TOKENS['IDENTIFIER']:
                    parameter = self.current_token

                    result.register_advancement()
                    self.advance()
                    self.skip_expression(result)

                    while (
                        self.current_token.type in (
                            TOKENS['AMPERSAND'],
                            TOKENS['COMMA'],
                            TOKENS['PIPE'],
                            TOKENS['DOUBLE_AMPERSAND'],
                            TOKENS['DOUBLE_PIPE']
                        ) or
                        self.current_token.match(TOKENS['KEYWORD'], 'and', 'or')
                    ):

                        result.register_advancement()
                        self.advance()
                        self.skip_expression(result)

                        if self.current_token.type != TOKENS['IDENTIFIER']:
                            return result.failure(self.new_error("expected identifier"))

                        targets.append(PysIdentifierNode(self.current_token))

                        result.register_advancement()
                        self.advance()
                        self.skip_expression(result)

                    if self.current_token.match(TOKENS['KEYWORD'], 'as'):
                        result.register_advancement()
                        self.advance()
                        self.skip_expression(result)

                        if self.current_token.type != TOKENS['IDENTIFIER']:
                            return result.failure(self.new_error("expected identifier"))

                    if self.current_token.type == TOKENS['IDENTIFIER']:
                        targets.insert(0, PysIdentifierNode(parameter))
                        parameter = self.current_token

                        result.register_advancement()
                        self.advance()
                        self.skip_expression(result)

                    else:
                        all_catch_handler = True

                else:
                    all_catch_handler = True

                if bracket:
                    self.close_bracket(result, left_bracket_token)
                    if result.error:
                        return result

                    self.bracket_level -= 1

                self.skip(result)

                catch_body = result.register(self.block_statements(), True)
                if result.error:
                    return result

                catch_cases.append(((tuple(targets), parameter), catch_body))
                advance_count = self.skip(result)

            if self.current_token.match(TOKENS['KEYWORD'], 'else'):
                result.register_advancement()
                self.advance()
                self.skip(result)

                else_body = result.register(self.block_statements(), True)
                if result.error:
                    return result

                advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'finally'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            finally_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        elif not catch_cases:
            return result.failure(self.new_error("expected 'catch', 'except', or 'finally'"))

        else:
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

    def with_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'with'):
            return result.failure(self.new_error("expected 'with'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        bracket = False

        if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
            bracket = True
            left_bracket_token = self.current_token
            self.bracket_level += 1

            result.register_advancement()
            self.advance()
            self.skip(result)

        contexts = []

        while True:
            context = result.register(self.single_expression(), True)
            if result.error:
                return result

            if self.current_token.match(TOKENS['KEYWORD'], 'as'):
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.new_error("expected identifier"))

            alias = None

            if self.current_token.type == TOKENS['IDENTIFIER']:
                alias = self.current_token

                result.register_advancement()
                self.advance()
                self.skip_expression(result)

            contexts.append((context, alias))

            if self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

            elif bracket and self.current_token.type == TOKENS['NULL']:
                break

            elif bracket and not is_right_bracket(self.current_token.type):
                return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

            else:
                break

        if bracket:
            self.close_bracket(result, left_bracket_token)
            if result.error:
                return result

            self.bracket_level -= 1

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        return result.success(
            PysWithNode(
                contexts,
                body,
                position
            )
        )

    def for_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'for'):
            return result.failure(self.new_error("expected 'for'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        bracket = False

        if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
            bracket = True
            left_bracket_token = self.current_token
            self.bracket_level += 1

            result.register_advancement()
            self.advance()
            self.skip(result)

        declaration = result.try_register(self.assignment_statement(self.primary))
        if result.error:
            return result

        if self.current_token.type == TOKENS['SEMICOLON']:
            foreach = False

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            condition = result.try_register(self.single_expression())
            if result.error:
                return result

            if self.current_token.type != TOKENS['SEMICOLON']:
                return result.failure(self.new_error("expected ';'"))

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            update = result.try_register(self.assignment_statement())
            if result.error:
                return result

        elif self.current_token.match(TOKENS['KEYWORD'], 'in', 'of'):
            if declaration is None:
                return result.failure(
                    self.new_error(
                        f"expected assign expression. Did you mean ';' instead of {self.current_token.value!r}?"
                    )
                )

            foreach = True

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            iteration = result.register(self.single_expression(), True)
            if result.error:
                return result

        elif declaration is None:
            return result.failure(self.new_error("expected assign expression or ';'"))

        else:
            return result.failure(self.new_error("expected 'in', 'of', or ';'"))

        if bracket:
            self.close_bracket(result, left_bracket_token)
            if result.error:
                return result

            self.bracket_level -= 1

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        else_body = None
        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'else'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            self.reverse(advance_count)

        return result.success(
            PysForNode(
                (declaration, iteration) if foreach else (declaration, condition, update),
                body,
                else_body,
                position
            )
        )

    def while_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'while'):
            return result.failure(self.new_error("expected 'while'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.walrus(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        else_body = None
        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'else'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            self.reverse(advance_count)

        return result.success(
            PysWhileNode(
                condition,
                body,
                else_body,
                position
            )
        )

    def do_while_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'do'):
            return result.failure(self.new_error("expected 'do'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], 'while'):
            return result.failure(self.new_error("expected 'while'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.walrus(), True)
        if result.error:
            return result

        else_body = None
        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'else'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            self.reverse(advance_count)

        return result.success(
            PysDoWhileNode(
                body,
                condition,
                else_body,
                position
            )
        )

    def repeat_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'repeat'):
            return result.failure(self.new_error("expected 'repeat'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.block_statements(), True)
        if result.error:
            return result

        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], 'until'):
            return result.failure(self.new_error("expected 'until'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.walrus(), True)
        if result.error:
            return result

        else_body = None
        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], 'else'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.block_statements(), True)
            if result.error:
                return result

        else:
            self.reverse(advance_count)

        return result.success(
            PysRepeatNode(
                body,
                condition,
                else_body,
                position
            )
        )

    def class_statement(self, decorators: Optional[list[PysNode]] = None) -> PysParserResult:
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], 'class'):
            return result.failure(self.new_error("expected 'class'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['IDENTIFIER']:
            return result.failure(self.new_error("expected identifier"))

        end = self.current_token.position.end
        name = self.current_token
        has_bases = False

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
            has_bases = True

            base = result.register(self.sequence_expression('tuple', should_sequence=True))
            if result.error:
                return result

            end = base.position.end
            bases = list(base.elements)

        elif self.current_token.match(TOKENS['KEYWORD'], 'extends'):
            has_bases = True

            result.register_advancement()
            self.advance()
            self.skip(result)

            base = result.register(self.expression(), True)
            if result.error:
                return result

            end = base.position.end
            bases = list(base.elements) if is_list(base.__class__) else [base]

        else:
            bases = []

        if self.current_token.type == TOKENS['COLON']:
            return result.failure(self.new_error("unlike python"))

        body = result.register(self.block_statements(), True)
        if result.error:
            return result.failure(
                self.new_error(
                    "expected statement, expression, '{', or ';'"
                    if has_bases else
                    "expected statement, expression, 'extends', '(', '{', or ';'"
                )
            )

        return result.success(
            PysClassNode(
                [] if decorators is None else decorators,
                name,
                bases,
                body,
                PysPosition(
                    self.current_token.position.file,
                    start,
                    end
                )
            )
        )

    def func_expression(self, decorators: Optional[list[PysNode]] = None) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position
        start = position.start
        constructor = False

        if self.current_token.match(TOKENS['KEYWORD'], 'constructor'):
            constructor = True
        elif not self.current_token.match(TOKENS['KEYWORD'], 'def', 'define', 'func', 'function'):
            return result.failure(self.new_error("expected 'def', 'define', 'func', 'function', or 'constructor'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        name = None
        parameters = []

        if constructor:
            name = PysToken(TOKENS['IDENTIFIER'], position, '__init__')
            parameters.append(PysToken(TOKENS['IDENTIFIER'], position, 'self'))

        elif self.current_token.type == TOKENS['IDENTIFIER']:
            name = self.current_token
            result.register_advancement()
            self.advance()
            self.skip(result)

        if self.current_token.type != TOKENS['LEFT_PARENTHESIS']:
            return result.failure(self.new_error("expected identifier or '('" if name is None else "expected '('"))

        left_bracket_token = self.current_token
        self.bracket_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        seen_keyword_argument = False

        while not is_right_bracket(self.current_token.type):

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.new_error("expected identifier"))

            key = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['EQUAL']:
                result.register_advancement()
                self.advance()
                self.skip(result)
                seen_keyword_argument = True

            elif seen_keyword_argument:
                return result.failure(self.new_error("expected '=' (follows keyword argument)"))

            if seen_keyword_argument:
                value = result.register(self.single_expression(), True)
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

            elif self.current_token.type == TOKENS['NULL']:
                break

            elif not is_right_bracket(self.current_token.type):
                return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end

        self.close_bracket(result, left_bracket_token)
        if result.error:
            return result

        self.bracket_level -= 1
        self.skip(result)

        if not constructor and self.current_token.type == TOKENS['EQUAL_ARROW']:
            position = self.current_token.position
            result.register_advancement()
            self.advance()
            self.skip(result)

            body = result.register(self.single_expression(), True)
            if result.error:
                return result

            body = PysReturnNode(body, position)

        elif self.current_token.type == TOKENS['COLON']:
            return result.failure(self.new_error("unlike python"))

        else:
            body = result.register(self.block_statements(), True)
            if result.error:
                return result.failure(
                    self.new_error(
                        "expected statement, expression, '{', or ';'"
                        if constructor else
                        "expected statement, expression, '{', ';', or '=>'"
                    )
                )

        self.skip_expression(result)

        return result.success(
            PysFunctionNode(
                [] if decorators is None else decorators,
                name,
                parameters,
                body,
                constructor,
                PysPosition(self.current_token.position.file, start, end)
            )
        )

    def return_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'return'):
            return result.failure(self.new_error("expected 'return'"))

        result.register_advancement()
        self.advance()

        value = result.try_register(self.expression())
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

    def global_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'global'):
            return result.failure(self.new_error("expected 'global'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        names = []
        bracket = False

        if self.current_token.type == TOKENS['LEFT_PARENTHESIS']:
            bracket = True
            left_bracket_token = self.current_token
            self.bracket_level += 1

            result.register_advancement()
            self.advance()
            self.skip(result)

        elif is_left_bracket(self.current_token.type):
            return result.failure(self.new_error(f"expected '(' not {chr(self.current_token.type)!r}"))

        if self.current_token.type != TOKENS['IDENTIFIER']:
            return result.failure(self.new_error("expected identifier"))

        while self.current_token.type == TOKENS['IDENTIFIER']:
            names.append(self.current_token)

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            if self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

            elif bracket and self.current_token.type == TOKENS['NULL']:
                break

            elif bracket and not is_right_bracket(self.current_token.type):
                return result.failure(self.new_error("invalid syntax. Perhaps you forgot a comma?"))

            else:
                break

        if bracket:
            self.close_bracket(result, left_bracket_token)
            if result.error:
                return result

            self.bracket_level -= 1

        return result.success(
            PysGlobalNode(
                names,
                position
            )
        )

    def del_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'del', 'delete'):
            return result.failure(self.new_error("expected 'del' or 'delete'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        targets = result.register(self.expression(), True)
        if result.error:
            return result

        return result.success(
            PysDeleteNode(
                list(targets.elements) if is_list(targets.__class__) else [targets],
                position
            )
        )

    def throw_statement(self) -> PysParserResult:
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], 'raise', 'throw'):
            return result.failure(self.new_error("expected 'raise' or 'throw'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.single_expression(), True)
        if result.error:
            return result

        primary = None

        if self.current_token.match(TOKENS['KEYWORD'], 'from'):
            result.register_advancement()
            self.advance()
            self.skip(result)

            primary = result.register(self.single_expression(), True)
            if result.error:
                return result

        return result.success(
            PysThrowNode(
                target,
                primary,
                position
            )
        )

    def assert_statement(self) -> PysParserResult:
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], 'assert'):
            return result.failure(self.new_error("expected 'assert'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.single_expression(), True)
        if result.error:
            return result

        message = None

        if self.current_token.type == TOKENS['COMMA']:
            result.register_advancement()
            self.advance()
            self.skip(result)

            message = result.register(self.single_expression(), True)
            if result.error:
                return result

        return result.success(
            PysAssertNode(
                condition,
                message
            )
        )

    def decorator(self) -> PysParserResult:
        result = PysParserResult()

        if self.current_token.type != TOKENS['AT']:
            return result.failure(self.new_error("expected '@'"))

        decorators = []

        while self.current_token.type == TOKENS['AT']:
            result.register_advancement()
            self.advance()

            decorators.append(result.register(self.walrus(), True))
            if result.error:
                return result

            self.skip(result, TOKENS['NEWLINE'], TOKENS['SEMICOLON'])

        if self.current_token.match(TOKENS['KEYWORD'], 'def', 'define', 'func', 'function'):
            func_expression = result.register(self.func_expression(decorators))
            if result.error:
                return result

            return result.success(func_expression)

        elif self.current_token.match(TOKENS['KEYWORD'], 'class'):
            class_expression = result.register(self.class_statement(decorators))
            if result.error:
                return result

            return result.success(class_expression)

        return result.failure(self.new_error("expected function or class declaration after decorator"))

    def block_statements(self) -> PysParserResult:
        result = PysParserResult()

        if self.current_token.type == TOKENS['LEFT_CURLY']:
            left_bracket_token = self.current_token

            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error:
                return result

            end = self.current_token.position.end

            self.close_bracket(result, left_bracket_token)
            if result.error:
                return result

            if isinstance(body, PysStatementsNode):
                setimuattr(
                    body, 'position',
                    PysPosition(
                        self.current_token.position.file,
                        left_bracket_token.position.start,
                        end
                    )
                )

            return result.success(body)

        elif self.current_token.type == TOKENS['SEMICOLON']:
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(
                PysStatementsNode(
                    [],
                    position
                )
            )

        elif self.current_token.type == TOKENS['COLON']:
            return result.failure(self.new_error("unlike python"))

        body = result.register(self.statement())
        if result.error:
            return result.failure(
                self.new_error("expected statement, expression, '{', or ';'"),
                fatal=False
            )

        return result.success(body)

    def chain_operator(
        self,
        function: Callable[[], PysParserResult],
        *operators: int | tuple[int, Any],
        membership: bool = False
    ) -> PysParserResult:
        result = PysParserResult()

        operations = []
        expressions = []

        expression = result.register(function())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operations.append(self.current_token)
            expressions.append(expression)

            if membership and self.current_token.match(TOKENS['KEYWORD'], 'not'):
                result.register_advancement()
                self.advance()
                self.skip_expression(result)

                if not self.current_token.match(TOKENS['KEYWORD'], 'in'):
                    return result.failure(self.new_error("expected 'in'"))

                operations[-1] = PysToken(
                    TOKENS['NOT_IN'],
                    self.current_token.position,
                    'not in'
                )

            last_token = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            if (
                membership and
                last_token.match(TOKENS['KEYWORD'], 'is') and
                self.current_token.match(TOKENS['KEYWORD'], 'not')
            ):
                operations[-1] = PysToken(
                    TOKENS['IS_NOT'],
                    self.current_token.position,
                    'is not'
                )

                result.register_advancement()
                self.advance()
                self.skip_expression(result)

            expression = result.register(function(), True)
            if result.error:
                return result

        if operations:
            expressions.append(expression)

        return result.success(
            PysChainOperatorNode(
                operations,
                expressions
            ) if operations else expression
        )

    def binary_operator(
        self,
        function: Callable[[], PysParserResult],
        *operators: int | tuple[int, Any]
    ) -> PysParserResult:
        result = PysParserResult()

        left = result.register(function())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expression(result)

            right = result.register(function(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def close_bracket(self, result: PysParserResult, left_bracket_token: PysToken) -> PysParserResult:
        if self.current_token.type != BRACKETS_MAP[left_bracket_token.type]:

            if is_right_bracket(self.current_token.type):
                result.failure(
                    self.new_error(
                        f"closing parenthesis {chr(self.current_token.type)!r} "
                        f"does not match opening parenthesis {chr(left_bracket_token.type)!r}"
                    )
                )

            elif self.current_token.type == TOKENS['NULL']:
                result.failure(
                    self.new_error(
                        f"{chr(left_bracket_token.type)!r} was never closed",
                        left_bracket_token.position
                    )
                )

            else:
                result.failure(self.new_error("invalid syntax"))

            return

        result.register_advancement()
        self.advance()

    def skip(self, result: PysParserResult, *types: int) -> int:
        types = types or (TOKENS['NEWLINE'],)
        count = 0

        while self.current_token.type in types:
            result.register_advancement()
            self.advance()
            count += 1

        return count

    def skip_expression(self, result: PysParserResult) -> int:
        return self.skip(result) if self.bracket_level > 0 else 0

    def proccess_future(self, name: str) -> PysParserResult:
        result = PysParserResult()

        if name == 'braces':
            return result.failure(self.new_error("yes, i use it for this language"))

        elif name == 'indent':
            return result.failure(self.new_error("not a chance"))

        elif name in ('dict_to_jsdict', 'dict2jsdict'):
            self.parser_flags |= DICT_TO_JSDICT
            return result.success(True)

        return result.failure(self.new_error(f"future feature {name} is not defined"))