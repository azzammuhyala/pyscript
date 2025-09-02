from .bases import Pys
from .context import PysContext
from .exceptions import PysException
from .constants import TOKENS
from .utils import SYNTAX
from .nodes import *

class PysParserResult(Pys):

    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count += 1
        self.advance_count += 1

    def register(self, result):
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        self.error = result.error

        return result.node

    def try_register(self, result):
        if result.error:
            self.to_reverse_count = result.advance_count
            return

        return self.register(result)

    def success(self, node):
        self.node = node

        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error

        return self

class PysParser(Pys):

    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1

        self.advance()

    def advance(self):
        self.token_index += 1
        self.update_current_token()

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def create_error(self, message, position=None):
        return PysException(
            SyntaxError(message),
            position or self.current_token.position,
            PysContext(None, self.current_token.file)
        )

    def parse(self, func=None):
        result = (func or self.statements)()

        if not result.error and self.current_token.type != TOKENS['EOF']:
            return result.failure(self.create_error("invalid syntax"))

        return result

    def statements(self):
        result = PysParserResult()
        start = self.current_token.position.start

        statements = []
        more_statements = True

        while True:
            count = self.skip(result, (TOKENS['NEWLINE'], TOKENS['SEMICOLON']))

            if not more_statements:
                more_statements = count

            if not more_statements:
                break

            statement = self.statement()
            if statement.error and str(statement.error) != "expected an expression or statement":
                return statement

            statement = result.try_register(statement)
            if statement:
                statements.append(statement)
            else:
                self.reverse(result.to_reverse_count)

            more_statements = False

        return result.success(
            PysSequenceNode(
                'statement',
                statements,
                PysPositionRange(
                    start,
                    self.current_token.position.end
                )
            )
        )

    def statement(self):
        result = PysParserResult()
        start = self.current_token.position.start

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['if']):
            if_expr = result.register(self.if_expr())
            if result.error:
                return result

            return result.success(if_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['switch']):
            switch_expr = result.register(self.switch_expr())
            if result.error:
                return result

            return result.success(switch_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['try']):
            try_expr = result.register(self.try_expr())
            if result.error:
                return result

            return result.success(try_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['for']):
            for_expr = result.register(self.for_expr())
            if result.error:
                return result

            return result.success(for_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['while']):
            while_expr = result.register(self.while_expr())
            if result.error:
                return result

            return result.success(while_expr)

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['return']):
            end = self.current_token.position.end

            result.register_advancement()
            self.advance()

            expr = result.try_register(self.expr())
            if expr:
                end = expr.position.end
            else:
                self.reverse(result.to_reverse_count)

            return result.success(
                PysReturnNode(
                    expr,
                    PysPositionRange(
                        start,
                        end
                    )
                )
            )

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['throw']):
            result.register_advancement()
            self.advance()

            expr = result.register(self.expr())
            if result.error:
                return result

            return result.success(
                PysThrowNode(
                    expr,
                    PysPositionRange(start, expr.position.end)
                )
            )

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['continue']):
            end = self.current_token.position.end

            result.register_advancement()
            self.advance()

            return result.success(
                PysContinueNode(
                    PysPositionRange(
                        start,
                        end
                    )
                )
            )

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['break']):
            end = self.current_token.position.end

            result.register_advancement()
            self.advance()

            return result.success(
                PysBreakNode(
                    PysPositionRange(
                        start,
                        end
                    )
                )
            )

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['del']):
            del_expr = result.register(self.del_expr())
            if result.error:
                return result

            return result.success(del_expr)

        expr = result.register(self.assign_expr())
        if result.error:
            return result.failure(self.create_error("expected an expression or statement"))

        return result.success(expr)

    def assign_expr(self):
        result = PysParserResult()

        variable = result.register(self.expr())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['EQ'],
            TOKENS['IPLUS'],
            TOKENS['IMINUS'],
            TOKENS['IMUL'],
            TOKENS['IDIV'],
            TOKENS['IFDIV'],
            TOKENS['IPOW'],
            TOKENS['IMOD'],
            TOKENS['IAND'],
            TOKENS['IOR'],
            TOKENS['IXOR'],
            TOKENS['ILSHIFT'],
            TOKENS['IRSHIFT']
        ):
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            value = result.register(self.expr())
            if result.error:
                return result

            variable = PysVariableAssignNode(variable, operand, value)

        return result.success(variable)

    def expr(self):
        result = PysParserResult()

        node = result.register(self.logic())
        if result.error:
            return result

        if self.current_token.type == TOKENS['QUESTION']:
            result.register_advancement()
            self.advance()

            valid = result.register(self.expr())
            if result.error:
                return result

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.create_error("expected ':'"))

            result.register_advancement()
            self.advance()

            invalid = result.register(self.expr())
            if result.error:
                return result

            return result.success(PysTernaryOperatorNode(node, valid, invalid))

        return result.success(node)

    def logic(self):
        result = PysParserResult()

        node = result.register(
            self.binary_operator(
                self.comp,
                (
                    (TOKENS['KEYWORD'], SYNTAX['keywords']['and']),
                    (TOKENS['KEYWORD'], SYNTAX['keywords']['or']),
                    (TOKENS['KEYWORD'], SYNTAX['keywords']['in']),
                    (TOKENS['KEYWORD'], SYNTAX['keywords']['is'])
                )
            )
        )

        if result.error:
            return result

        return result.success(node)

    def comp(self):
        result = PysParserResult()

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['not']):
            operand = self.current_token

            result.register_advancement()
            self.advance()

            node = result.register(self.comp())
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    operand,
                    node
                )
            )

        node = result.register(
            self.binary_operator(
                self.bitwise,
                (TOKENS['EE'], TOKENS['CE'], TOKENS['NE'], TOKENS['LT'], TOKENS['GT'], TOKENS['LTE'], TOKENS['GTE'])
            )
        )

        if result.error:
            return result

        return result.success(node)

    def bitwise(self):
        return self.binary_operator(
            self.arith,
            (TOKENS['AND'], TOKENS['OR'], TOKENS['XOR'], TOKENS['LSHIFT'], TOKENS['RSHIFT'])
        )

    def arith(self):
        return self.binary_operator(self.term, (TOKENS['PLUS'], TOKENS['MINUS']))

    def term(self):
        return self.binary_operator(self.factor, (TOKENS['MUL'], TOKENS['DIV'], TOKENS['FDIV'], TOKENS['MOD']))

    def factor(self):
        result = PysParserResult()
        token = self.current_token

        if token.type in (TOKENS['PLUS'], TOKENS['MINUS'], TOKENS['NOT'], TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            factor = result.register(self.factor())
            if result.error:
                return result

            return result.success(PysUnaryOperatorNode(token, factor))

        return self.power()

    def power(self):
        result = PysParserResult()

        left = result.register(self.primary())
        if result.error:
            return result

        if self.current_token.type == TOKENS['POW']:
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            right = result.register(self.factor())
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def primary(self):
        result = PysParserResult()
        start = self.current_token.position.start

        node = result.register(self.atom())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['DOT'], TOKENS['LSQUARE'], TOKENS['LPAREN'], TOKENS['INCREMENT'], TOKENS['DECREMENT']
        ):

            if self.current_token.type == TOKENS['DOT']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                attribute = self.current_token
                start = self.current_token.position.start

                if attribute.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.create_error("expected identifier"))

                result.register_advancement()
                self.advance()

                node = PysAttributeNode(node, PysVariableAccessNode(attribute))

            elif self.current_token.type == TOKENS['LSQUARE']:
                start = self.current_token.position.start

                result.register_advancement()
                self.advance()
                self.skip(result)

                slice = []
                index = []

                if self.current_token.type == TOKENS['COLON']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    index.append(None)

                else:
                    expr = result.register(self.expr())
                    if result.error:
                        return result

                    index.append(expr)

                is_slice = self.current_token.type == TOKENS['COLON']

                while len(index) < 3 and self.current_token.type == TOKENS['COLON']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    if self.current_token.type == TOKENS['RSQUARE']:
                        break

                    if self.current_token.type == TOKENS['COLON']:
                        index.append(None)

                    else:
                        expr = result.register(self.expr())
                        if result.error:
                            return result

                        index.append(expr)

                    self.skip(result)

                if not is_slice:
                    slice.append(index[0])
                elif len(index) == 1:
                    slice.append((None, index[0], None))
                else:
                    slice.append(tuple(index) + (None,) if len(index) == 2 else tuple(index))

                index.clear()

                should_sequence = self.current_token.type == TOKENS['COMMA']

                while self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    if self.current_token.type == TOKENS['RSQUARE']:
                        break

                    if self.current_token.type == TOKENS['COLON']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        index.append(None)

                    else:
                        expr = result.register(self.expr())
                        if result.error:
                            return result

                        index.append(expr)

                    is_slice = self.current_token.type == TOKENS['COLON']

                    while len(index) < 3 and self.current_token.type == TOKENS['COLON']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        if self.current_token.type == TOKENS['RSQUARE']:
                            break

                        if self.current_token.type == TOKENS['COLON']:
                            index.append(None)

                        else:
                            expr = result.register(self.expr())
                            if result.error:
                                return result

                            index.append(expr)

                        self.skip(result)

                    if not is_slice:
                        slice.append(index[0])
                    elif len(index) == 1:
                        slice.append((None, index[0], None))
                    else:
                        slice.append(tuple(index) + (None,) if len(index) == 2 else tuple(index))

                    index.clear()

                self.skip(result)

                if self.current_token.type != TOKENS['RSQUARE']:
                    return result.failure(self.create_error("expected ']'"))

                end = self.current_token.position.end

                result.register_advancement()
                self.advance()

                if not should_sequence:
                    slice = slice[0]

                node = PysSubscriptNode(node, slice, PysPositionRange(start, end))

                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['LPAREN']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                args = []

                if self.current_token.type != TOKENS['RPAREN']:
                    on_keyword_state = False

                    arg_or_key = result.register(self.expr())
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['EQ']:
                        if not isinstance(arg_or_key, PysVariableAccessNode):
                            return result.failure(self.create_error("expected identifier", arg_or_key.position))

                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        on_keyword_state = True

                    if on_keyword_state:
                        value = result.register(self.expr())
                        if result.error:
                            return result.failure(self.create_error("expected expression"))

                        args.append((arg_or_key, value))
                    else:
                        args.append(arg_or_key)

                    self.skip(result)

                    while self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        if self.current_token.type == TOKENS['RPAREN']:
                            break

                        arg_or_key = result.register(self.expr())
                        if result.error:
                            return result

                        if on_keyword_state and not isinstance(arg_or_key, PysVariableAccessNode):
                            return result.failure(self.create_error("expected identifier", arg_or_key.position))

                        self.skip(result)

                        if self.current_token.type == TOKENS['EQ']:
                            result.register_advancement()
                            self.advance()
                            self.skip(result)

                            on_keyword_state = True

                            value = result.register(self.expr())
                            if result.error:
                                return result.failure(self.create_error("expected expression"))

                            self.skip(result)

                            args.append((arg_or_key, value))

                        elif on_keyword_state and self.current_token.type != TOKENS['EQ']:
                            return result.failure(self.create_error("expected '='"))

                        else:
                            args.append(arg_or_key)

                    self.skip(result)

                    if self.current_token.type != TOKENS['RPAREN']:
                        return result.failure(
                            self.create_error("expected ',' or ')'. Did you forgot comma or closing bracket?")
                        )

                end = self.current_token.position.end

                result.register_advancement()
                self.advance()

                node = PysCallNode(node, args, PysPositionRange(start, end))
                start = self.current_token.position.start

            elif self.current_token.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
                operand = self.current_token
                result.register_advancement()
                self.advance()

                node = PysUnaryOperatorNode(operand, node, operand_position='right')
                start = self.current_token.position.start

        return result.success(node)

    def atom(self):
        result = PysParserResult()
        token = self.current_token

        if token.type == TOKENS['NUMBER']:
            result.register_advancement()
            self.advance()

            return result.success(PysNumberNode(token))

        elif token.type == TOKENS['STRING']:
            result.register_advancement()
            self.advance()

            return result.success(PysStringNode(token))

        elif token.type == TOKENS['IDENTIFIER']:
            result.register_advancement()
            self.advance()

            return result.success(PysVariableAccessNode(token))

        elif token.type == TOKENS['LPAREN']:
            expr = result.register(self.sequence_expr('tuple'))
            if result.error:
                return result

            return result.success(expr)

        elif token.type == TOKENS['LSQUARE']:
            list_expr = result.register(self.sequence_expr('list'))
            if result.error:
                return result

            return result.success(list_expr)

        elif token.type == TOKENS['LBRACE']:
            result_dict = self.sequence_expr('dict')
            dict_expr = result.try_register(result_dict)

            if not dict_expr:
                if str(result_dict.error) != "expected ':'":
                    return result_dict

                self.reverse(result.to_reverse_count)

                set_expr = result.register(self.sequence_expr('set'))
                if result.error:
                    return result

                return result.success(set_expr)

            return result.success(dict_expr)

        elif token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['func']):
            func_def = result.register(self.func_expr())
            if result.error:
                return result

            return result.success(func_def)

        return result.failure(self.create_error("expected expression", token.position))

    def if_expr(self):
        result = PysParserResult()

        all_cases = result.register(self.if_expr_cases(SYNTAX['keywords']['if']))
        if result.error:
            return result

        return result.success(PysIfNode(all_cases[0], all_cases[1]))

    def elif_expr(self):
        return self.if_expr_cases(SYNTAX['keywords']['elif'])

    def else_expr(self):
        result = PysParserResult()
        else_case = None

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['LBRACE']:
                return result.failure(self.create_error("expected '{'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            statements = result.register(self.statements())
            if result.error:
                return result

            self.skip(result)

            else_case = statements

            if self.current_token.type != TOKENS['RBRACE']:
                return result.failure(self.create_error("expected '}'"))

            result.register_advancement()
            self.advance()

        return result.success(else_case)

    def elif_or_else_expr(self):
        result = PysParserResult()
        cases, else_case = [], None

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['elif']):
            all_cases = result.register(self.elif_expr())
            if result.error:
                return result

            cases, else_case = all_cases

        else:
            else_case = result.register(self.else_expr())
            if result.error:
                return result

        return result.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        result = PysParserResult()
        cases, else_case = [], None

        if not self.current_token.match(TOKENS['KEYWORD'], case_keyword):
            return result.failure(self.create_error("expected '{}'".format(case_keyword)))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.create_error("expected '('"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.expr())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RPAREN']:
            return result.failure(self.create_error("expected ')'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        cases.append((condition, body))

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        result.register_advancement()
        self.advance()

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], (SYNTAX['keywords']['elif'], SYNTAX['keywords']['else'])):
            all_cases = result.register(self.elif_or_else_expr())
            if result.error:
                return result

            new_cases, else_case = all_cases
            cases.extend(new_cases)
        else:
            self.reverse(advance_count)

        return result.success((cases, else_case))

    def switch_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['switch']):
            return result.failure(self.create_error("expected '{}'".format(SYNTAX['keywords']['switch'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.create_error("expected '('"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.expr())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RPAREN']:
            return result.failure(self.create_error("expected ')'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        switch_cases = result.register(self.case_or_default_expr())
        if result.error:
            return result

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        result.register_advancement()
        self.advance()

        return result.success(PysSwitchNode(expr, *switch_cases))

    def case_expr(self):
        return self.cases_expr(SYNTAX['keywords']['case'])

    def default_expr(self):
        result = PysParserResult()
        default_case = None

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['default']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.create_error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            body = result.register(self.statements())
            if result.error:
                return result

            default_case = body

        return result.success(default_case)

    def case_or_default_expr(self):
        result = PysParserResult()
        cases, default_case = [], None

        if self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['case']):
            all_cases = result.register(self.case_expr())
            if result.error:
                return result

            cases, default_case = all_cases

        else:
            default_case = result.register(self.default_expr())
            if result.error:
                return result

        return result.success((cases, default_case))

    def cases_expr(self, case_keyword):
        result = PysParserResult()
        cases, default_case = [], None

        if not self.current_token.match(TOKENS['KEYWORD'], case_keyword):
            return result.failure(self.create_error("expected '{}'".format(case_keyword)))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.expr())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['COLON']:
            return result.failure(self.create_error("expected ':'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        cases.append((expr, body))

        if self.current_token.match(TOKENS['KEYWORD'], (SYNTAX['keywords']['case'], SYNTAX['keywords']['default'])):
            all_cases = result.register(self.case_or_default_expr())
            if result.error:
                return result

            new_cases, default_case = all_cases
            cases.extend(new_cases)

        return result.success((cases, default_case))

    def for_expr(self):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['for']):
            return result.failure(self.create_error("expected 'for'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.create_error("expected '('"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        init_token = self.current_token
        init = result.try_register(self.assign_expr())

        self.skip(result)

        if self.current_token.type == TOKENS['SEMICOLON']:
            foreach = False

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['SEMICOLON']:
                condition = None
            else:
                condition = result.register(self.expr())
                if result.error:
                    return result

            if self.current_token.type != TOKENS['SEMICOLON']:
                return result.failure(self.create_error("expected ';'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['RPAREN']:
                update = None
            else:
                update = result.register(self.assign_expr())
                if result.error:
                    return result

        elif self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['of']):
            if init is None:
                return result.failure(self.create_error("expected expression", init_token.position))

            foreach = True

            result.register_advancement()
            self.advance()
            self.skip(result)

            iterable = result.register(self.expr())
            if result.error:
                return result

        else:
            return result.failure(self.create_error("expected 'of' or ';'"))

        self.skip(result)

        if self.current_token.type != TOKENS['RPAREN']:
            return result.failure(self.create_error("expected ')'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        end = self.current_token.position.end

        result.register_advancement()
        self.advance()

        return result.success(
            PysForNode(
                (init, iterable) if foreach else (init, condition, update),
                body,
                PysPositionRange(start, end)
            )
        )

    def while_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['while']):
            return result.failure(self.create_error("expected 'while'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.create_error("expected '('"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.expr())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RPAREN']:
            return result.failure(self.create_error("expected ')'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()

        body = result.register(self.statements())
        if result.error:
            return result

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        result.register_advancement()
        self.advance()

        return result.success(PysWhileNode(condition, body))

    def del_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['del']):
            return result.failure(self.create_error("expected 'del'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.expr())
        if result.error:
            return result

        return result.success(PysDeleteNode(expr.elements if isinstance(expr, PysSequenceNode) else [expr]))

    def func_expr(self):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['func']):
            return result.failure(self.create_error("expected '{}'".format(SYNTAX['keywords']['func'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['IDENTIFIER']:
            name = PysVariableAccessNode(self.current_token)

            result.register_advancement()
            self.advance()

        else:
            name = None

        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.create_error("expected identifier or '('"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        parameters = []

        if self.current_token.type != TOKENS['RPAREN']:
            on_keyword_state = False

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.create_error("expected identifier"))

            key = PysVariableAccessNode(self.current_token)

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['EQ']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                on_keyword_state = True

            if on_keyword_state:
                value = result.register(self.expr())
                if result.error:
                    return result.failure(self.create_error("expected expression"))

                parameters.append((key, value))
            else:
                parameters.append(key)

            while self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == TOKENS['RPAREN']:
                    break

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.create_error("expected identifier"))

                key = PysVariableAccessNode(self.current_token)

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == TOKENS['EQ']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    on_keyword_state = True

                    value = result.register(self.expr())
                    if result.error:
                        return result.failure(self.create_error("expected expression"))

                    self.skip(result)

                    parameters.append((key, value))

                elif on_keyword_state and self.current_token.type != TOKENS['EQ']:
                    return result.failure(self.create_error("expected '='"))

                else:
                    parameters.append(key)

            self.skip(result)

            if self.current_token.type != TOKENS['RPAREN']:
                return result.failure(
                    self.create_error("expected ',' or ')'. Did you forgot comma or closing bracket?")
                )

        end_parameter = self.current_token.position.end

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        end = self.current_token.position.end

        result.register_advancement()
        self.advance()

        return result.success(
            PysFunctionNode(
                name,
                parameters,
                body,
                PysPositionRange(start, end),
                PysPositionRange(start, end_parameter)
            )
        )

    def try_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['try']):
            return result.failure(self.create_error("expected '{}'".format(SYNTAX['keywords']['try'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        try_body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], SYNTAX['keywords']['catch']):
            return result.failure(self.create_error("expected '{}'".format(SYNTAX['keywords']['catch'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LPAREN']:
            result.register_advancement()
            self.advance()
            self.skip(result)
            
            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.create_error("expected identifier"))

            variable = PysVariableAccessNode(self.current_token)

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['RPAREN']:
                return result.failure(self.create_error("expected ')'"))

            result.register_advancement()
            self.advance()
            self.skip(result)
        else:
            variable = None

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.create_error("expected '{'"))

        result.register_advancement()
        self.advance()
        self.skip(result)

        catch_body = result.register(self.statements())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['RBRACE']:
            return result.failure(self.create_error("expected '}'"))

        result.register_advancement()
        self.advance()

        return result.success(PysTryNode(try_body, variable, catch_body))

    def sequence_expr(self, type):
        result = PysParserResult()
        start = self.current_token.position.start

        should_sequence = True
        elements = []

        if type == 'tuple':
            prefix = TOKENS['LPAREN']
            suffix = TOKENS['RPAREN']
            characters = '()'
        elif type == 'list':
            prefix = TOKENS['LSQUARE']
            suffix = TOKENS['RSQUARE']
            characters = '[]'
        elif type in ('dict', 'set'):
            prefix = TOKENS['LBRACE']
            suffix = TOKENS['RBRACE']
            characters = '{}'

        if self.current_token.type != prefix:
            return result.failure(self.create_error("expected '{}'".format(characters[0])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == suffix:
            end = self.current_token.position.end

            result.register_advancement()
            self.advance()

        elif type == 'dict':
            key = result.register(self.expr())
            if result.error:
                return result.failure(self.create_error("expected expression"))

            self.skip(result)

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.create_error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            value = result.register(self.expr())
            if result.error:
                return result.failure(self.create_error("expected expression"))

            elements.append((key, value))

            self.skip(result)

            while self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == suffix:
                    break

                key = result.register(self.expr())
                if result.error:
                    return result.failure(self.create_error("expected expression"))

                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    return result.failure(self.create_error("expected ':'"))

                result.register_advancement()
                self.advance()
                self.skip(result)

                value = result.register(self.expr())
                if result.error:
                    return result.failure(self.create_error("expected expression"))

                self.skip(result)

                elements.append((key, value))

            if self.current_token.type != suffix:
                return result.failure(
                    self.create_error(
                        "expected ',' or '{}'. Did you forgot comma or closing bracket?".format(characters[1])
                    )
                )

            end = self.current_token.position.end
            result.register_advancement()
            self.advance()

        else:
            elements.append(result.register(self.expr()))
            if result.error:
                return result

            self.skip(result)

            should_sequence = self.current_token.type == TOKENS['COMMA']

            while self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type == suffix:
                    break

                expr = result.try_register(self.expr())
                if not expr:
                    break

                elements.append(expr)

                self.skip(result)

            self.skip(result)

            if self.current_token.type != suffix:
                return result.failure(
                    self.create_error(
                        "expected ',' or '{}'. Did you forgot comma or closing bracket?".format(characters[1])
                    )
                )

            end = self.current_token.position.end

            result.register_advancement()
            self.advance()

        if type == 'tuple' and not should_sequence:
            return result.success(elements[0])

        return result.success(
            PysSequenceNode(
                type,
                elements,
                PysPositionRange(start, end)
            )
        )

    def skip(self, result, types=TOKENS['NEWLINE']):
        if not isinstance(types, tuple):
            types = (types,)

        count = 0

        while self.current_token.type in types:
            result.register_advancement()
            self.advance()
            count += 1

        return count

    def binary_operator(self, func_left, operators, func_right=None):
        result = PysParserResult()

        if func_right is None:
            func_right = func_left

        left = result.register(func_left())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operand = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            right = result.register(func_right())
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)