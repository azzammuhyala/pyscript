from .bases import Pys
from .context import PysContext
from .exceptions import PysException
from .nodes import *

def check_valid_assign(self, node, message):
    if isinstance(node, PysSequenceNode):
        for n in node.elements:
            check_valid_assign(self, n, message)
            if self.error:
                return self.error

    elif not isinstance(node, (PysVariableAccessNode, PysAttributeNode, PysSubscriptNode)):
        return self.throw(message, node.position)

class PysValidator(Pys):

    def __init__(self, file):
        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0
        self.error = None
        self.file = file

    def throw(self, message, position):
        if self.error is None:
            self.error = PysException(
                SyntaxError(message),
                position,
                PysContext(None, self.file)
            )

        return self.error

    def visit(self, node):
        func = getattr(self, 'visit_' + type(node).__name__[3:], None)
        if self.error:
            return self.error

        if func:
            return func(node)

    def visit_SequenceNode(self, node):
        if node.type == 'statement':
            for element in node.elements:
                self.visit(element)
                if self.error:
                    return self.error

    def visit_VariableAssignNode(self, node):
        return check_valid_assign(
            self,
            node.variable,
            "cannot assign to expression here. Maybe you meant '==' instead of '='?"
        )

    def visit_IfNode(self, node: PysIfNode):
        for _, body in node.cases:
            self.visit(body)
            if self.error:
                return self.error

        if node.else_case:
            self.visit(node.else_case)
            if self.error:
                return self.error

    def visit_SwitchNode(self, node):
        self.in_switch += 1

        for _, body in node.cases:
            self.visit(body)
            if self.error:
                return self.error

        if node.default_case:
            self.visit(node.default_case)
            if self.error:
                return self.error

        self.in_switch -= 1

    def visit_ForNode(self, node):
        self.in_loop += 1

        if len(node.iterable) == 2:
            check_valid_assign(self, node.iterable[0], "cannot assign to expression")
            if self.error:
                return self.error

        self.visit(node.body)
        if self.error:
            return self.error

        self.in_loop -= 1

    def visit_WhileNode(self, node):
        self.in_loop += 1

        self.visit(node.body)
        if self.error:
            return self.error

        self.in_loop -= 1

    def visit_FunctionNode(self, node):
        in_loop, in_function, in_switch = self.in_loop, self.in_function, self.in_switch

        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0

        self.in_function += 1

        names = set()

        for element in node.parameter:
            node_name = element[0] if isinstance(element, tuple) else element
            name = node_name.name.value

            if name in names:
                return self.throw(f"duplicate argument '{name}' in function definition", node_name.position)

            names.add(name)

        self.visit(node.body)
        if self.error:
            return self.error

        self.in_function -= 1

        self.in_loop = in_loop
        self.in_function = in_function
        self.in_switch = in_switch

    def visit_CallNode(self, node):
        names = set()

        for element in node.args:
            if isinstance(element, tuple):
                node_name = element[0]
                name = node_name.name.value

                if name in names:
                    return self.throw(f"duplicate argument '{name}' in call definition", node_name.position)

                names.add(name)

    def visit_BreakNode(self, node):
        if self.in_loop == 0 and self.in_switch == 0:
            return self.throw("break outside of loop or switch case", node.position)

    def visit_ContinueNode(self, node):
        if self.in_loop == 0:
            return self.throw("continue outside of loop", node.position)

    def visit_ReturnNode(self, node):
        if self.in_function == 0:
            return self.throw("return outside of function", node.position)

    def visit_DeleteNode(self, node):
        for element in node.objects:
            if not isinstance(element, (PysAttributeNode, PysVariableAccessNode, PysSubscriptNode)):
                return self.throw("cannot delete literal", element.position)