from .bases import Pys
from .constants import TOKENS, DEFAULT, NSEQ_GLOBAL, NSEQ_DEL, NSEQ_DICT, NTER_GENERAL
from .context import PysContext
from .exceptions import PysException
from .nodes import PysNode, PysKeywordNode, PysIdentifierNode, PysSequenceNode, PysAttributeNode, PysSubscriptNode
from .position import PysPosition
from .utils.decorators import typechecked

from typing import Optional

class PysAnalyzer(Pys):

    @typechecked
    def __init__(
        self,
        node: PysNode,
        flags: int = DEFAULT,
        context_parent: Optional[PysContext] = None,
        context_parent_entry_position: Optional[PysPosition] = None
    ) -> None:

        self.node = node
        self.flags = flags
        self.context = context_parent
        self.context_parent_entry_position = context_parent_entry_position

    def throw(self, message, position):
        if self.error is None:
            self.error = PysException(
                SyntaxError(message),
                PysContext(
                    file=self.node.position.file,
                    flags=self.flags,
                    parent=self.context,
                    parent_entry_position=self.context_parent_entry_position
                ),
                position
            )

    @typechecked
    def analyze(self) -> PysException | None:
        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0
        self.error = None

        self.visit(self.node)
        return self.error

    def visit(self, node):
        func = getattr(self, 'visit_' + type(node).__name__[3:], None)
        if not self.error and func:
            func(node)

    def visit_SequenceNode(self, node):

        if node.type == NSEQ_DEL:

            for element in node.elements:

                if isinstance(element, PysAttributeNode):
                    self.visit(element.target)
                    if self.error:
                        return

                elif isinstance(element, PysSubscriptNode):
                    self.visit(element.target)
                    if self.error:
                        return

                    self.visit_slice_SubscriptNode(element.slice)
                    if self.error:
                        return

                elif isinstance(element, PysKeywordNode):
                    self.throw(f"cannot delete {element.token.value}", element.position)
                    return

                elif not isinstance(element, PysIdentifierNode):
                    self.throw("cannot delete literal", element.position)
                    return

        elif node.type == NSEQ_GLOBAL:

            if self.in_function == 0:
                self.throw("global outside of function", node.position)

        elif node.type == NSEQ_DICT:

            for key, value in node.elements:

                self.visit(key)
                if self.error:
                    return

                self.visit(value)
                if self.error:
                    return

        else:

            for element in node.elements:
                self.visit(element)
                if self.error:
                    return

    def visit_AttributeNode(self, node):
        self.visit(node.target)

    def visit_SubscriptNode(self, node):
        self.visit(node.target)
        if self.error:
            return

        self.visit_slice_SubscriptNode(node.slice)

    def visit_ChainOperatorNode(self, node):
        for expression in node.expressions:
            self.visit(expression)
            if self.error:
                return

    def visit_TernaryOperatorNode(self, node):
        if node.style == NTER_GENERAL:
            self.visit(node.condition)
            if self.error:
                return

            self.visit(node.valid)
            if self.error:
                return

        else:
            self.visit(node.valid)
            if self.error:
                return

            self.visit(node.condition)
            if self.error:
                return

        self.visit(node.invalid)

    def visit_BinaryOperatorNode(self, node):
        self.visit(node.left)
        if self.error:
            return

        self.visit(node.right)

    def visit_UnaryOperatorNode(self, node):
        if node.operand.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            operator = 'increase' if node.operand.type == TOKENS['INCREMENT'] else 'decrease'

            if isinstance(node.value, PysKeywordNode):
                self.throw(f"cannot {operator} {node.value.token.value}", node.value.position)
                return

            elif not isinstance(node.value, (PysIdentifierNode, PysAttributeNode, PysSubscriptNode)):
                self.throw(f"cannot {operator} literal", node.value.position)
                return

        self.visit(node.value)

    def visit_AssignNode(self, node):
        self.visit_declaration_AssignNode(
            node.target,
            "cannot assign to expression here. Maybe you meant '==' instead of '='?"
        )

        if self.error:
            return

        self.visit(node.value)

    def visit_IfNode(self, node):
        for condition, body in node.cases_body:
            self.visit(condition)
            if self.error:
                return

            self.visit(body)
            if self.error:
                return

        if node.else_body:
            self.visit(node.else_body)

    def visit_SwitchNode(self, node):
        self.visit(node.target)
        if self.error:
            return

        self.in_switch += 1

        for condition, body in node.case_cases:
            self.visit(condition)
            if self.error:
                return

            self.visit(body)
            if self.error:
                return

        if node.default_body:
            self.visit(node.default_body)
            if self.error:
                return

        self.in_switch -= 1

    def visit_TryNode(self, node):
        self.visit(node.body)
        if self.error:
            return

        for _, body in node.catch_cases:
            self.visit(body)
            if self.error:
                return

        if node.else_body:
            self.visit(node.else_body)
            if self.error:
                return

        if node.finally_body:
            self.visit(node.finally_body)

    def visit_WithNode(self, node):
        self.visit(node.context)
        if self.error:
            return

        self.visit(node.body)

    def visit_ForNode(self, node):
        if len(node.header) == 2:
            declaration, iterable = node.header

            self.visit_declaration_AssignNode(declaration, "cannot assign to expression")
            if self.error:
                return

            self.visit(iterable)
            if self.error:
                return

        elif len(node.header) == 3:
            for element in node.header:
                self.visit(element)
                if self.error:
                    return

        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        if self.error:
            return

        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_DoWhileNode(self, node):
        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        self.visit(node.condition)
        if self.error:
            return

        if node.else_body:
            self.visit(node.else_body)

    def visit_ClassNode(self, node):
        for decorator in node.decorators:
            self.visit(decorator)
            if self.error:
                return

        for base in node.bases:
            self.visit(base)
            if self.error:
                return

        in_loop, in_function, in_switch = self.in_loop, self.in_function, self.in_switch

        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0

        self.visit(node.body)
        if self.error:
            return

        self.in_loop = in_loop
        self.in_function = in_function
        self.in_switch = in_switch

    def visit_FunctionNode(self, node):
        for decorator in node.decorators:
            self.visit(decorator)
            if self.error:
                return

        parameter_names = set()

        for element in node.parameters:
            token = (element[0] if isinstance(element, tuple) else element)
            name = token.value

            if name in parameter_names:
                return self.throw(f"duplicate argument {name!r} in function definition", token.position)

            parameter_names.add(name)

            if isinstance(element, tuple):
                self.visit(element[1])
                if self.error:
                    return

        in_loop, in_switch = self.in_loop, self.in_switch

        self.in_loop = 0
        self.in_switch = 0

        self.in_function += 1

        self.visit(node.body)
        if self.error:
            return

        self.in_function -= 1

        self.in_loop = in_loop
        self.in_switch = in_switch

    def visit_CallNode(self, node):
        self.visit(node.target)
        if self.error:
            return

        keyword_argument_names = set()

        for element in node.arguments:

            if isinstance(element, tuple):
                token, value = element
                name = token.value

                if name in keyword_argument_names:
                    self.throw(f"duplicate argument {name!r} in call definition", token.position)
                    return

                keyword_argument_names.add(name)

            else:
                value = element

            self.visit(value)
            if self.error:
                return

    def visit_ReturnNode(self, node):
        if self.in_function == 0:
            self.throw("return outside of function", node.position)
            return

        if node.value:
            self.visit(node.value)

    def visit_ThrowNode(self, node):
        self.visit(node.target)

    def visit_AssertNode(self, node):
        self.visit(node.condition)
        if self.error:
            return

        if node.message:
            self.visit(node.message)

    def visit_ContinueNode(self, node):
        if self.in_loop == 0:
            self.throw("continue outside of loop", node.position)

    def visit_BreakNode(self, node):
        if self.in_loop == 0 and self.in_switch == 0:
            self.throw("break outside of loop or switch case", node.position)

    def visit_slice_SubscriptNode(self, nslice):
        if isinstance(nslice, tuple):
            for element in nslice:
                self.visit_slice_SubscriptNode(element)
                if self.error:
                    return

        elif isinstance(nslice, slice):
            if nslice.start is not None:
                self.visit(nslice.start)
                if self.error:
                    return

            if nslice.stop is not None:
                self.visit(nslice.stop)
                if self.error:
                    return

            if nslice.step is not None:
                self.visit(nslice.step)
                if self.error:
                    return

        else:
            self.visit(nslice)

    def visit_declaration_AssignNode(self, node, message):
        if isinstance(node, PysAttributeNode):
            self.visit(node.target)

        elif isinstance(node, PysSubscriptNode):
            self.visit(node.target)
            if self.error:
                return

            self.visit_slice_SubscriptNode(node.slice)

        elif isinstance(node, PysSequenceNode):
            for element in node.elements:
                self.visit_declaration_AssignNode(element, message)
                if self.error:
                    return

        elif isinstance(node, PysKeywordNode):
            self.throw(f"cannot assign to {node.token.value}", node.position)

        elif not isinstance(node, PysIdentifierNode):
            self.throw(message, node.position)