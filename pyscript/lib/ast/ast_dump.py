from pyscript.core.nodes import *
from pyscript.core.utils.string import indent

from typing import Any, Optional, Sequence

PARENTHESIS_TYPES_MAP = {
    tuple: '()',
    list: '[]',
    set: '{}',
    dict: '{}',
    slice: ('slice(', ')')
}

class DumpNode:

    def __init__(
        self,
        annotate_fields: bool = True,
        include_attributes: bool = False,
        indent: Optional[int] = None,
        show_empty: bool = False
    ) -> None:

        if not isinstance(indent, (type(None), int)):
            raise TypeError("dump() or DumpNode(): indent is not integer or NoneType")

        self.annotate_fields = bool(annotate_fields)
        self.include_attributes = bool(include_attributes)
        self.indent = indent
        self.show_empty = bool(show_empty)

    def _format_parameter(self, name: str, value: str) -> str:
        return f'{name}={value}' if self.annotate_fields else value

    def _format_parameters(self, parameters: Sequence[str], add_comma: bool = False) -> str:
        if self.indent is None or not parameters:
            string = ', '.join(parameters)
            if add_comma:
                string += ','

        else:
            string = ','.join('\n' + indent(parameter, self.indent) for parameter in parameters)
            if add_comma:
                string += ','
            if parameters:
                string += '\n'

        return string

    def _node_representation(self, node: PysNode, parameters_info: list[tuple[str, PysNode | Any]]) -> str:
        parameters = [
            self._format_parameter(name, self.visit(value))
            for name, value in parameters_info
            if self.show_empty or value is not None
        ]

        if self.include_attributes:
            parameters.append(self._format_parameter('position_start', repr(node.position.start)))
            parameters.append(self._format_parameter('position_end', repr(node.position.end)))

        name = type(node).__name__.removeprefix('Pys').removesuffix('Node')
        formatted_parameters = self._format_parameters(parameters)

        return f'{name}({formatted_parameters})'

    def _any_representation(self, object: Any) -> str:
        type_object = type(object)
        if type_object not in PARENTHESIS_TYPES_MAP:
            return repr(object)

        if type_object is slice:
            parameters = [
                self._format_parameter('start', self.visit(object.start)),
                self._format_parameter('stop', self.visit(object.stop)),
                self._format_parameter('step', self.visit(object.step))
            ]
        elif type_object is dict:
            parameters = [f'{self.visit(key)}: {self.visit(value)}' for key, value in object.items()]
        else:
            parameters = tuple(map(self.visit, object))

        open_parenthesis, close_parenthesis = PARENTHESIS_TYPES_MAP[type_object]
        formatted_parameters = self._format_parameters(
            parameters,
            add_comma=type_object is tuple and len(object) == 1
        )

        return f'{open_parenthesis}{formatted_parameters}{close_parenthesis}'

    def visit(self, node: PysNode) -> str:
        return getattr(self, 'visit_' + type(node).__name__.removeprefix('Pys'), self._any_representation)(node)

    def visit_NumberNode(self, node: PysNumberNode) -> str:
        return self._node_representation(
            node,
            [
                ('value', node.value)
            ]
        )

    def visit_StringNode(self, node: PysStringNode) -> str:
        return self._node_representation(
            node,
            [
                ('value', node.value)
            ]
        )

    def visit_KeywordNode(self, node: PysKeywordNode) -> str:
        return self._node_representation(
            node,
            [
                ('name', node.name)
            ]
        )

    def visit_IdentifierNode(self, node: PysIdentifierNode) -> str:
        return self._node_representation(
            node,
            [
                ('name', node.name)
            ]
        )

    def visit_DictionaryNode(self, node: PysDictionaryNode) -> str:
        return self._node_representation(
            node,
            [
                ('pairs', node.pairs),
                ('class_type', node.class_type.__name__)
            ]
        )

    def visit_SetNode(self, node: PysSetNode) -> str:
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_ListNode(self, node: PysListNode) -> str:
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_TupleNode(self, node: PysTupleNode) -> str:
        return self._node_representation(
            node,
            [
                ('elements', node.elements)
            ]
        )

    def visit_AttributeNode(self, node: PysAttributeNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('attribute', node.attribute)
            ]
        )

    def visit_SubscriptNode(self, node: PysSubscriptNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('slice', node.slice)
            ]
        )

    def visit_CallNode(self, node: PysCallNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('arguments', node.arguments)
            ]
        )

    def visit_ChainOperatorNode(self, node: PysChainOperatorNode) -> str:
        return self._node_representation(
            node,
            [
                ('operations', node.operations),
                ('expressions', node.expressions)
            ]
        )

    def visit_TernaryOperatorNode(self, node: PysTernaryOperatorNode) -> str:
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('valid', node.valid),
                ('invalid', node.invalid),
                ('style', node.style)
            ]
        )

    def visit_BinaryOperatorNode(self, node: PysBinaryOperatorNode) -> str:
        return self._node_representation(
            node,
            [
                ('left', node.left),
                ('operand', node.operand),
                ('right', node.right)
            ]
        )

    def visit_UnaryOperatorNode(self, node: PysUnaryOperatorNode) -> str:
        return self._node_representation(
            node,
            [
                ('operand', node.operand),
                ('value', node.value)
            ]
        )

    def visit_IncrementalNode(self, node: PysIncrementalNode) -> str:
        return self._node_representation(
            node,
            [
                ('operand', node.operand),
                ('target', node.target),
                ('operand_position', node.operand_position)
            ]
        )

    def visit_StatementsNode(self, node: PysStatementsNode) -> str:
        return self._node_representation(
            node,
            [
                ('body', node.body)
            ]
        )

    def visit_AssignmentNode(self, node: PysAssignmentNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('operand', node.operand),
                ('value', node.value)
            ]
        )

    def visit_ImportNode(self, node: PysImportNode) -> str:
        return self._node_representation(
            node,
            [
                ('name', node.name),
                ('packages', node.packages)
            ]
        )

    def visit_IfNode(self, node: PysIfNode) -> str:
        return self._node_representation(
            node,
            [
                ('cases_body', node.cases_body),
                ('else_body', node.else_body)
            ]
        )

    def visit_SwitchNode(self, node: PysSwitchNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('case_cases', node.case_cases),
                ('default_body', node.default_body)
            ]
        )

    def visit_MatchNode(self, node: PysMatchNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('cases', node.cases),
                ('default', node.default)
            ]
        )

    def visit_TryNode(self, node: PysTryNode) -> str:
        return self._node_representation(
            node,
            [
                ('body', node.body),
                ('catch_cases', node.catch_cases),
                ('else_body', node.else_body),
                ('finally_body', node.finally_body)
            ]
        )

    def visit_WithNode(self, node: PysWithNode) -> str:
        return self._node_representation(
            node,
            [
                ('contexts', node.contexts),
                ('body', node.body)
            ]
        )

    def visit_ForNode(self, node: PysForNode) -> str:
        return self._node_representation(
            node,
            [
                ('header', node.header),
                ('body', node.body),
                ('else_body', node.else_body)
            ]
        )

    def visit_WhileNode(self, node: PysWhileNode) -> str:
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('body', node.body),
                ('else_body', node.else_body)
            ]
        )

    def visit_DoWhileNode(self, node: PysDoWhileNode) -> str:
        return self._node_representation(
            node,
            [
                ('body', node.body),
                ('condition', node.condition),
                ('else_body', node.else_body)
            ]
        )

    def visit_RepeatNode(self, node: PysRepeatNode) -> str:
        return self._node_representation(
            node,
            [
                ('body', node.body),
                ('condition', node.condition),
                ('else_body', node.else_body)
            ]
        )

    def visit_ClassNode(self, node: PysClassNode) -> str:
        return self._node_representation(
            node,
            [
                ('decorators', node.decorators),
                ('name', node.name),
                ('bases', node.bases),
                ('body', node.body)
            ]
        )

    def visit_FunctionNode(self, node: PysFunctionNode) -> str:
        return self._node_representation(
            node,
            [
                ('decorators', node.decorators),
                ('name', node.name),
                ('parameters', node.parameters),
                ('body', node.body),
                ('constructor', node.constructor)
            ]
        )

    def visit_GlobalNode(self, node: PysGlobalNode) -> str:
        return self._node_representation(
            node,
            [
                ('identifiers', node.identifiers)
            ]
        )

    def visit_ReturnNode(self, node: PysReturnNode) -> str:
        return self._node_representation(
            node,
            [
                ('value', node.value)
            ]
        )

    def visit_ThrowNode(self, node: PysThrowNode) -> str:
        return self._node_representation(
            node,
            [
                ('target', node.target),
                ('primary', node.primary)
            ]
        )

    def visit_AssertNode(self, node: PysAssertNode) -> str:
        return self._node_representation(
            node,
            [
                ('condition', node.condition),
                ('message', node.message)
            ]
        )

    def visit_DeleteNode(self, node: PysDeleteNode) -> str:
        return self._node_representation(
            node,
            [
                ('targets', node.targets)
            ]
        )

    def visit_EllipsisNode(self, node: PysEllipsisNode) -> str:
        return self._node_representation(node, [])

    def visit_ContinueNode(self, node: PysContinueNode) -> str:
        return self._node_representation(node, [])

    def visit_BreakNode(self, node: PysBreakNode) -> str:
        return self._node_representation(node, [])

def dump(
    node: PysNode,
    *,
    annotate_fields: bool = True,
    include_attributes: bool = False,
    indent: Optional[int] = None,
    show_empty: bool = False
) -> str:
    return DumpNode(
        annotate_fields=annotate_fields,
        include_attributes=include_attributes,
        indent=indent,
        show_empty=show_empty
    ).visit(node)