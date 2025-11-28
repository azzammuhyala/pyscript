from pyscript.core.nodes import *

PARENTHESIS_TYPES_MAP = {
    tuple: '()',
    list: '[]',
    set: '{}',
    dict: '{}',
    slice: ('slice(', ')')
}

def walk(node):

    if isinstance(node, PysDictionaryNode):
        yield node

        for key, value in node.pairs:
            yield from walk(key)
            yield from walk(value)

    elif isinstance(node, (PysSetNode, PysListNode, PysTupleNode)):
        yield node

        for element in node.elements:
            yield from walk(element)

    elif isinstance(node, PysAttributeNode):
        yield node
        yield from walk(node.target)

    elif isinstance(node, PysSubscriptNode):
        yield node
        yield from walk(node.target)

        if isinstance(node.slice, slice):
            if node.slice.start:
                yield from walk(node.slice.start)
            if node.slice.stop:
                yield from walk(node.slice.stop)
            if node.slice.step:
                yield from walk(node.slice.step)

        elif isinstance(node.slice, tuple):
            for index in node.slice:
                if isinstance(index, slice):
                    if index.start:
                        yield from walk(index.start)
                    if index.stop:
                        yield from walk(index.stop)
                    if index.step:
                        yield from walk(index.step)
                else:
                    yield from walk(index)

        else:
            yield from walk(node.slice)

    elif isinstance(node, PysCallNode):
        yield node
        yield from walk(node.target)

        for argument in node.arguments:
            if isinstance(argument, tuple):
                yield from walk(argument[1])
            else:
                yield from walk(argument)

    elif isinstance(node, PysChainOperatorNode):
        yield node

        for expression in node.expressions:
            yield from walk(expression)

    elif isinstance(node, PysTernaryOperatorNode):
        yield node

        if node.style == 'general':
            yield from walk(node.condition)
            yield from walk(node.valid)
        elif node.style == 'pythonic':
            yield from walk(node.valid)
            yield from walk(node.condition)
        else:
            raise ValueError(f"invalid PysTernaryOperatorNode.style named {node.style!r}")

        yield from walk(node.invalid)

    elif isinstance(node, PysBinaryOperatorNode):
        yield node
        yield from walk(node.left)
        yield from walk(node.right)

    elif isinstance(node, PysUnaryOperatorNode):
        yield node

        if node.operand_position not in ('left', 'right'):
            raise ValueError(f"invalid PysUnaryOperatorNode.operand_position named {node.operand_position!r}")

        yield from walk(node.value)

    elif isinstance(node, PysStatementsNode):
        yield node

        for statement in node.body:
            yield from walk(statement)

    elif isinstance(node, PysAssignNode):
        yield node
        yield from walk(node.target)
        yield from walk(node.value)

    elif isinstance(node, PysImportNode):
        yield node

    elif isinstance(node, PysIfNode):
        yield node

        for condition, body in node.cases_body:
            yield from walk(condition)
            yield from walk(body)

        if node.else_body:
            yield from walk(node.else_body)

    elif isinstance(node, PysSwitchNode):
        yield node
        yield from walk(node.target)

        for condition, body in node.case_cases:
            yield from walk(condition)
            yield from walk(body)

        if node.default_body:
            yield from walk(node.default_body)

    elif isinstance(node, PysTryNode):
        yield node
        yield from walk(node.body)

        for (error, parameter), body in node.catch_cases:
            if error:
                yield from walk(error)
            yield from walk(body)

        if node.else_body:
            yield from walk(node.else_body)

        if node.finally_body:
            yield from walk(node.finally_body)

    elif isinstance(node, PysWithNode):
        yield node
        yield from walk(node.context)
        yield from walk(node.body)

    elif isinstance(node, PysForNode):
        yield node

        if len(node.header) == 2:
            yield from walk(node.header[0])
            yield from walk(node.header[1])

        elif len(node.header) == 3:
            for part in node.header:
                if part:
                    yield from walk(part)

        else:
            raise TypeError("invalid PysForNode.header")

        yield from walk(node.body)

        if node.else_body:
            yield from walk(node.else_body)

    elif isinstance(node, PysWhileNode):
        yield node
        yield from walk(node.condition)
        yield from walk(node.body)

        if node.else_body:
            yield from walk(node.else_body)

    elif isinstance(node, PysDoWhileNode):
        yield node
        yield from walk(node.body)
        yield from walk(node.condition)

        if node.else_body:
            yield from walk(node.else_body)

    elif isinstance(node, PysClassNode):
        yield node

        for decorator in node.decorators:
            yield from walk(decorator)

        for base in node.bases:
            yield from walk(base)

        yield from walk(node.body)

    elif isinstance(node, PysFunctionNode):
        yield node

        for decorator in node.decorators:
            yield from walk(decorator)

        for parameter in node.parameters:
            if isinstance(parameter, tuple):
                yield from walk(parameter[1])

        yield from walk(node.body)

    elif isinstance(node, PysGlobalNode):
        yield node

    elif isinstance(node, PysReturnNode):
        yield node
        if node.value:
            yield from walk(node.value)

    elif isinstance(node, PysThrowNode):
        yield node
        yield from walk(node.target)

        if node.another:
            yield from walk(node.another)

    elif isinstance(node, PysAssertNode):
        yield node
        yield from walk(node.condition)

        if node.message:
            yield from walk(node.message)

    elif isinstance(node, PysDeleteNode):
        yield node

        for target in node.targets:
            yield from walk(target)

    elif isinstance(node, PysNode):
        yield node

    else:
        raise TypeError("unknown Node")

class DumpNode:

    def __init__(
        self,
        annotate_fields=True,
        include_attributes=False,
        indent=None,
        show_empty=False
    ):
        if not isinstance(indent, (type(None), int)):
            raise TypeError("dump() or DumpNode(): indent is not integer or NoneType")

        self.annotate_fields = bool(annotate_fields)
        self.include_attributes = bool(include_attributes)
        self.indent = indent
        self.show_empty = bool(show_empty)

        self._deep = 0

    def _padding(self, index):
        if self.indent is None:
            return '' if index == 0 else ' '
        deep = self._deep + index if index < 0 else self._deep
        return '\n' + ' ' * (self.indent * deep)

    def _format_parameter(self, name, value):
        return f'{name}={value}' if self.annotate_fields else value

    def _node_representation(self, node, parameters):
        formatted_parameters = []

        for name, value in parameters:
            if self.show_empty or value is not None:
                formatted_parameters.append(
                    self._format_parameter(
                        name,
                        self.visit(value)
                    )
                )

        if self.include_attributes:
            formatted_parameters.append(self._format_parameter('position_start', repr(node.position.start)))
            formatted_parameters.append(self._format_parameter('position_end', repr(node.position.end)))

        suffix_parameter = (
            ''
            if self.indent is None or not formatted_parameters else
            self._padding(-1)
        )

        formatted_parameters = ','.join(
            self._padding(i) + parameter
            for i, parameter in enumerate(formatted_parameters)
        )

        return f'{type(node).__name__[3:-4]}({formatted_parameters}{suffix_parameter})'

    def _any_representation(self, object):
        type_object = type(object)

        if type_object not in PARENTHESIS_TYPES_MAP:
            return repr(object)

        open_parenthesis, close_parenthesis = PARENTHESIS_TYPES_MAP[type_object]

        if type_object is slice:
            object_length = 3
            formatted_parameters = ','.join(
                self._padding(i) + child
                for i, child in enumerate([
                    self._format_parameter('start', self.visit(object.start)),
                    self._format_parameter('stop', self.visit(object.stop)),
                    self._format_parameter('step', self.visit(object.step))
                ])
            )

        elif type_object is dict:
            object_length = len(object)
            formatted_parameters = ','.join(
                self._padding(i) + self.visit(key) + ': ' + self.visit(value)
                for i, (key, value) in enumerate(object.items())
            )

        else:
            object_length = len(object)
            formatted_parameters = ','.join(
                self._padding(i) + self.visit(child)
                for i, child in enumerate(object)
            ) 

        suffix_parameter = ',' if type_object is tuple and object_length == 1 else ''
        if self.indent is not None and object_length:
            suffix_parameter += self._padding(-1)

        return f'{open_parenthesis}{formatted_parameters}{suffix_parameter}{close_parenthesis}'

    def visit(self, node):
        method = getattr(self, f'visit_{type(node).__name__[3:]}', self._any_representation)

        if self.indent is None:
            return method(node)

        self._deep += 1
        result = method(node)
        self._deep -= 1

        return result

    def visit_NumberNode(self, node):
        return self._node_representation(
            node,
            [
                ('value', node.token.value)
            ]
        )

    def visit_StringNode(self, node):
        return self._node_representation(
            node,
            [
                ('value', node.token.value)
            ]
        )

    def visit_KeywordNode(self, node):
        return self._node_representation(
            node,
            [
                ('name', node.token.value)
            ]
        )

    def visit_IdentifierNode(self, node):
        return self._node_representation(
            node,
            [
                ('name', node.token.value)
            ]
        )

    def visit_DictionaryNode(self, node):
        return self._node_representation(
            node,
            [
                ('pairs', node.pairs)
            ]
        )

    def visit_SetNode(self, node):
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_ListNode(self, node):
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_TupleNode(self, node):
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_AttributeNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('attribute', node.attribute)
            ]
        )

    def visit_SubscriptNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('slice', node.slice)
            ]
        )

    def visit_CallNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('arguments', node.arguments)
            ]
        )

    def visit_ChainOperatorNode(self, node):
        return self._node_representation(
            node,
            [
                ('operations', node.operations),
                ('expressions', node.expressions)
            ]
        )

    def visit_TernaryOperatorNode(self, node):
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('valid', node.valid),
                ('invalid', node.invalid),
                ('style', node.style)
            ]
        )

    def visit_BinaryOperatorNode(self, node):
        return self._node_representation(
            node,
            [
                ('left', node.left),
                ('operand', node.operand),
                ('right', node.right)
            ]
        )

    def visit_UnaryOperatorNode(self, node):
        return self._node_representation(
            node,
            [
                ('operand', node.operand),
                ('value', node.value),
                ('operand_position', node.operand_position)
            ]
        )

    def visit_StatementsNode(self, node):
        return self._node_representation(
            node,
            [
                ('body', node.body)
            ]
        )

    def visit_AssignNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('operand', node.operand),
                ('value', node.value)
            ]
        )

    def visit_ImportNode(self, node):
        return self._node_representation(
            node,
            [
                ('name', node.name),
                ('packages', node.packages)
            ]
        )

    def visit_IfNode(self, node):
        return self._node_representation(
            node,
            [
                ('cases_body', node.cases_body),
                ('else_body', node.else_body)
            ]
        )

    def visit_SwitchNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('case_cases', node.case_cases),
                ('default_body', node.default_body)
            ]
        )

    def visit_TryNode(self, node):
        return self._node_representation(
            node,
            [
                ('body', node.body),
                ('catch_cases', node.catch_cases),
                ('else_body', node.else_body),
                ('finally_body', node.finally_body)
            ]
        )

    def visit_WithNode(self, node):
        return self._node_representation(
            node,
            [
                ('context', node.context),
                ('alias', node.alias),
                ('body', node.body)
            ]
        )

    def visit_ForNode(self, node):
        return self._node_representation(
            node,
            [
                ('header', node.header),
                ('body', node.body),
                ('else_body', node.else_body)
            ]
        )

    def visit_WhileNode(self, node):
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('body', node.body),
                ('else_body', node.else_body)
            ]
        )

    def visit_DoWhileNode(self, node):
        return self._node_representation(
            node,
            [
                ('body', node.body),
                ('condition', node.condition),
                ('else_body', node.else_body)
            ]
        )

    def visit_ClassNode(self, node):
        return self._node_representation(
            node,
            [
                ('decorators', node.decorators),
                ('name', node.name),
                ('bases', node.bases),
                ('body', node.body)
            ]
        )

    def visit_FunctionNode(self, node):
        return self._node_representation(
            node,
            [
                ('decorators', node.decorators),
                ('name', node.name),
                ('parameters', node.parameters),
                ('body', node.body)
            ]
        )

    def visit_GlobalNode(self, node):
        return self._node_representation(
            node,
            [
                ('identifiers', node.identifiers)
            ]
        )

    def visit_ReturnNode(self, node):
        return self._node_representation(
            node,
            [
                ('value', node.value)
            ]
        )

    def visit_ThrowNode(self, node):
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('another', node.another)
            ]
        )

    def visit_AssertNode(self, node):
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('message', node.message)
            ]
        )

    def visit_DeleteNode(self, node):
        return self._node_representation(
            node,
            [
                ('targets', node.targets)
            ]
        )

    def visit_EllipsisNode(self, node):
        return self._node_representation(node, [])

    def visit_ContinueNode(self, node):
        return self._node_representation(node, [])

    def visit_BreakNode(self, node):
        return self._node_representation(node, [])

def dump(
    node,
    *,
    annotate_fields=True,
    include_attributes=False,
    indent=None,
    show_empty=False
):
    return DumpNode(
        annotate_fields=annotate_fields,
        include_attributes=include_attributes,
        indent=indent,
        show_empty=show_empty
    ).visit(node)