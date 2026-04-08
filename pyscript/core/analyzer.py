from .bases import Pys
from .checks import is_sequence
from .constants import DEFAULT
from .context import PysContext
from .exceptions import PysTraceback
from .nodes import *
from .position import PysPosition
from .token import TOKENS
from .utils.decorators import typecheck

from typing import Optional

class PysAnalyzer(Pys):

    @typecheck
    def __init__(
        self,
        node: PysNode,
        flags: int = DEFAULT,
        context_parent: Optional[PysContext] = None,
        context_parent_entry_position: Optional[PysPosition] = None
    ) -> None:

        self.node = node
        self.flags = flags
        self.context_parent = context_parent
        self.context_parent_entry_position = context_parent_entry_position

    @typecheck
    def analyze(self) -> PysTraceback | None:
        self.in_loop = 0
        self.in_function = 0
        self.in_class = 0
        self.in_switch = 0
        self.function_parameters = set()
        self.error = None

        self.visit(self.node)
        return self.error

    def throw(self, message: str, position: PysPosition) -> None:
        if self.error is None:
            self.error = PysTraceback(
                SyntaxError(message),
                PysContext(
                    file=self.node.position.file,
                    flags=self.flags,
                    parent=self.context_parent,
                    parent_entry_position=self.context_parent_entry_position
                ),
                position
            )

    def visit(self, node: PysNode) -> None:
        func = getattr(self, 'visit_' + type(node).__name__.removeprefix('Pys'), None)
        if not self.error and func:
            func(node)

    def visit_DictionaryNode(self, node: PysDictionaryNode) -> None:
        for key, value in node.pairs:

            self.visit(key)
            if self.error:
                return

            self.visit(value)
            if self.error:
                return

    def visit_SetNode(self, node: PysSetNode) -> None:
        for element in node.elements:
            self.visit(element)
            if self.error:
                return

    def visit_ListNode(self, node: PysListNode) -> None:
        for element in node.elements:
            self.visit(element)
            if self.error:
                return

    def visit_TupleNode(self, node: PysTupleNode) -> None:
        for element in node.elements:
            self.visit(element)
            if self.error:
                return

    def visit_AttributeNode(self, node: PysAttributeNode) -> None:
        self.visit(node.target)

    def visit_SubscriptNode(self, node: PysSubscriptNode) -> None:
        self.visit(node.target)
        if self.error:
            return

        self.visit_slice_from_SubscriptNode(node.slice)

    def visit_CallNode(self, node: PysCallNode) -> None:
        self.visit(node.target)
        if self.error:
            return

        keyword_names = set()

        for element in node.arguments:

            if element.__class__ is tuple:
                token, value = element
                name = token.value
                if name in keyword_names:
                    self.throw(f"duplicate argument {name!r} in call definition", token.position)
                    return
                keyword_names.add(name)

            else:
                value = element

            self.visit(value)
            if self.error:
                return

    def visit_ChainOperatorNode(self, node: PysChainOperatorNode) -> None:
        for expression in node.expressions:
            self.visit(expression)
            if self.error:
                return

    def visit_TernaryOperatorNode(self, node: PysTernaryOperatorNode) -> None:
        if node.style == 'general':
            self.visit(node.condition)
            if self.error:
                return

            self.visit(node.valid)
            if self.error:
                return

            self.visit(node.invalid)

        elif node.style == 'pythonic':
            self.visit(node.valid)
            if self.error:
                return

            self.visit(node.condition)
            if self.error:
                return

            self.visit(node.invalid)

    def visit_BinaryOperatorNode(self, node: PysBinaryOperatorNode) -> None:
        self.visit(node.left)
        if self.error:
            return

        self.visit(node.right)

    def visit_UnaryOperatorNode(self, node: PysUnaryOperatorNode) -> None:
        self.visit(node.value)

    def visit_IncrementalNode(self, node: PysIncrementalNode) -> None:
        operator = 'increase' if node.operand.type == TOKENS['DOUBLE_PLUS'] else 'decrease'
        self.visit_declaration_from_AssignmentNode(node.target, f"cannot {operator} literal", operator)

    def visit_StatementsNode(self, node: PysStatementsNode) -> None:
        for element in node.body:
            self.visit(element)
            if self.error:
                return

    def visit_AssignmentNode(self, node: PysAssignmentNode) -> None:
        self.visit_declaration_from_AssignmentNode(
            node.target,
            "cannot assign to expression here. Maybe you meant '==' instead of '='?"
        )
        if self.error:
            return

        self.visit(node.value)

    def visit_IfNode(self, node: PysIfNode) -> None:
        for condition, body in node.cases_body:
            self.visit(condition)
            if self.error:
                return

            self.visit(body)
            if self.error:
                return

        if node.else_body:
            self.visit(node.else_body)

    def visit_SwitchNode(self, node: PysSwitchNode) -> None:
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

    def visit_MatchNode(self, node: PysMatchNode) -> None:
        if node.target:
            self.visit(node.target)
            if self.error:
                return

        for condition, value in node.cases:
            self.visit(condition)
            if self.error:
                return

            self.visit(value)
            if self.error:
                return

        if node.default:
            self.visit(node.default)

    def visit_TryNode(self, node: PysTryNode) -> None:
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

    def visit_WithNode(self, node: PysWithNode) -> None:
        for context, _ in node.contexts:
            self.visit(context)
            if self.error:
                return

        self.visit(node.body)

    def visit_ForNode(self, node: PysForNode) -> None:
        if len(node.header) == 2:
            declaration, iteration = node.header

            self.visit_declaration_from_AssignmentNode(declaration, "cannot assign to expression")
            if self.error:
                return

            self.visit(iteration)
            if self.error:
                return

        elif len(node.header) == 3:
            for element in node.header:
                self.visit(element)
                if self.error:
                    return

        self.in_loop += 1

        self.visit(node.body)
        if self.error:
            return

        self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_WhileNode(self, node: PysWhileNode) -> None:
        self.visit(node.condition)
        if self.error:
            return

        self.in_loop += 1

        self.visit(node.body)
        if self.error:
            return

        self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_DoWhileNode(self, node: PysDoWhileNode) -> None:
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

    def visit_RepeatNode(self, node: PysRepeatNode) -> None:

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

    def visit_ClassNode(self, node: PysClassNode) -> None:
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

        self.in_class += 1

        self.visit(node.body)
        if self.error:
            return

        self.in_class -= 1

        self.in_loop = in_loop
        self.in_function = in_function
        self.in_switch = in_switch

    def visit_FunctionNode(self, node: PysFunctionNode) -> None:
        if node.constructor and self.in_class == 0:
            self.throw("constructor function outside of class", node.name.position)
            return

        for decorator in node.decorators:
            self.visit(decorator)
            if self.error:
                return

        parameter_names = set()

        for element in node.parameters:
            is_keyword = element.__class__ is tuple
            token = element[0] if is_keyword else element
            name = token.value

            if name in parameter_names:
                return self.throw(f"duplicate argument {name!r} in function definition", token.position)

            parameter_names.add(name)

            if is_keyword:
                self.visit(element[1])
                if self.error:
                    return

        in_loop, in_class, in_switch, parameters = self.in_loop, self.in_class, self.in_switch, self.function_parameters

        self.in_loop = 0
        self.in_class = 0
        self.in_switch = 0

        self.in_function += 1
        self.function_parameters = parameter_names

        self.visit(node.body)
        if self.error:
            return

        self.in_function -= 1
        self.function_parameters = parameters

        self.in_loop = in_loop
        self.in_class = in_class
        self.in_switch = in_switch

    def visit_GlobalNode(self, node: PysGlobalNode) -> None:
        if self.in_function == 0:
            self.throw("global outside of function", node.position)

        for identifier in node.identifiers:
            if identifier.value in self.function_parameters:
                self.throw(f"name {identifier.value!r} is parameter and global", identifier.position)
                return

    def visit_ReturnNode(self, node: PysReturnNode) -> None:
        if self.in_function == 0:
            self.throw("return outside of function", node.position)
            return

        if node.value:
            self.visit(node.value)

    def visit_ThrowNode(self, node: PysThrowNode) -> None:
        self.visit(node.target)
        if self.error:
            return

        if node.primary:
            self.visit(node.primary)

    def visit_AssertNode(self, node: PysAssertNode) -> None:
        self.visit(node.condition)
        if self.error:
            return

        if node.message:
            self.visit(node.message)

    def visit_DeleteNode(self, node: PysDeleteNode) -> None:
        for target in node.targets:
            type = target.__class__

            if type is PysAttributeNode:
                self.visit(target.target)
                if self.error:
                    return

            elif type is PysSubscriptNode:
                self.visit(target.target)
                if self.error:
                    return

                self.visit_slice_from_SubscriptNode(target.slice)
                if self.error:
                    return

            elif type is PysKeywordNode:
                self.throw(f"cannot delete {target.name.value}", target.position)
                return

            elif type is PysDebugNode:
                self.throw("cannot delete to __debug__", node.position)
                return

            elif type is not PysIdentifierNode:
                self.throw("cannot delete literal", target.position)
                return

    def visit_ContinueNode(self, node: PysContinueNode) -> None:
        if self.in_loop == 0:
            self.throw("continue outside of loop", node.position)

    def visit_BreakNode(self, node: PysBreakNode) -> None:
        if self.in_loop == 0 and self.in_switch == 0:
            self.throw("break outside of loop or switch case", node.position)

    def visit_slice_from_SubscriptNode(self, node: PysNode | slice | tuple[PysNode | slice, ...]) -> None:
        type = node.__class__

        if type is slice:
            if node.start is not None:
                self.visit(node.start)
                if self.error:
                    return

            if node.stop is not None:
                self.visit(node.stop)
                if self.error:
                    return

            if node.step is not None:
                self.visit(node.step)
                if self.error:
                    return

        elif type is tuple:
            for element in node:
                self.visit_slice_from_SubscriptNode(element)
                if self.error:
                    return

        else:
            self.visit(node)

    def visit_declaration_from_AssignmentNode(
        self,
        node: PysIdentifierNode | PysAttributeNode | PysSubscriptNode | PysSetNode | PysListNode | PysTupleNode,
        message: str,
        operator_name: str = 'assign'
    ) -> None:

        type = node.__class__

        if type is PysAttributeNode:
            self.visit(node.target)

        elif type is PysSubscriptNode:
            self.visit(node.target)
            if self.error:
                return

            self.visit_slice_from_SubscriptNode(node.slice)

        elif is_sequence(type):
            for element in node.elements:
                self.visit_declaration_from_AssignmentNode(element, message, operator_name)
                if self.error:
                    return

        elif type is PysKeywordNode:
            self.throw(f"cannot {operator_name} to {node.name.value}", node.position)

        elif type is PysDebugNode:
            self.throw(f"cannot {operator_name} to __debug__", node.position)

        elif type is not PysIdentifierNode:
            self.throw(message, node.position)