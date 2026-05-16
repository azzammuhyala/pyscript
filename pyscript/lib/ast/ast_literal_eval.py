from pyscript.core.interpreter import get_value_from_keyword
from pyscript.core.mapping import GET_BINARY_FUNCTION, GET_UNARY_FUNCTION
from pyscript.core.nodes import (
    PysNode, PysNumberNode, PysStringNode, PysKeywordNode, PysIdentifierNode, PysDictionaryNode, PysSetNode,
    PysListNode, PysTupleNode, PysCallNode, PysUnaryOperatorNode, PysBinaryOperatorNode, PysEllipsisNode
)
from pyscript.core.position import PysPosition
from pyscript.core.pysbuiltins import pys_builtins
from pyscript.core.token import TOKENS, REVERSE_TOKENS

from types import EllipsisType
from typing import Any, Callable

is_arithmetic = frozenset([TOKENS['PLUS'], TOKENS['MINUS']]).__contains__

get_identifier = {
    'Ellipsis': pys_builtins.Ellipsis,
    'NotImplemented': pys_builtins.NotImplemented,
    'inf': pys_builtins.inf,
    'infj': pys_builtins.infj,
    'nan': pys_builtins.nan,
    'nanj': pys_builtins.nanj
}.get

def _error(exception: type[BaseException] | BaseException, position: PysPosition) -> BaseException:
    return (
        exception(f'(ln {position.start_line}, col {position.start_column})')
        if isinstance(exception, type) else
        type(exception)(f'{exception} (ln {position.start_line}, col {position.start_column})')
    )

def visit(node: PysNode) -> Any:
    return get_visitor(node.__class__)(node)

def visit_unknown_node(node: PysNode) -> None:
    raise _error(ValueError(f"invalid node: {type(node).__name__}"), node.position)

def visit_NumberNode(node: PysNumberNode) -> int | float | complex:
    return node.value.value

def visit_StringNode(node: PysStringNode) -> str | bytes:
    return node.value.value

def visit_KeywordNode(node: PysKeywordNode) -> bool | None:
    #      vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv <- always boolean or none
    return get_value_from_keyword(node.name.value)

def visit_IdentifierNode(node: PysIdentifierNode) -> Any:
    name = node.name.value
    value = get_identifier(name)
    if value is None:
        raise _error(ValueError(f"invalid identifier: {name}"), node.position)
    return value

def visit_DictionaryNode(node: PysDictionaryNode) -> dict:
    return {visit(key): visit(value) for key, value in node.pairs}

def visit_SetNode(node: PysSetNode) -> set:
    return set(map(visit, node.elements))

def visit_ListNode(node: PysListNode) -> list:
    return list(map(visit, node.elements))

def visit_TupleNode(node: PysTupleNode) -> tuple:
    return tuple(map(visit, node.elements))

def visit_CallNode(node: PysCallNode) -> set:
    target = node.target
    if isinstance(target, PysIdentifierNode) and target.name.value == 'set' and not node.arguments:
        return set()
    raise _error(ValueError("invalid call node except for 'set()'"), node.position)

def visit_UnaryOperatorNode(node: PysUnaryOperatorNode) -> Any:
    operand = node.operand.type
    if is_arithmetic(operand):
        return GET_UNARY_FUNCTION(operand)(visit(node.value))
    raise _error(ValueError(f"invalid unary operator node: {REVERSE_TOKENS[operand]}"), node.position)

def visit_BinaryOperatorNode(node: PysBinaryOperatorNode) -> Any:
    operand = node.operand.type
    if is_arithmetic(operand):
        return GET_BINARY_FUNCTION(operand)(visit(node.left), visit(node.right))
    raise _error(ValueError(f"invalid binary operator node: {REVERSE_TOKENS[operand]}"), node.position)

def visit_EllipsisNode(node: PysEllipsisNode) -> EllipsisType:
    return ...

get_visitor: Callable[[type[PysNode]], Callable[[PysNode], Any]] = {
    class_node: globals().get('visit_' + class_node.__name__.removeprefix('Pys'), visit_unknown_node)
    for class_node in PysNode.__subclasses__()
}.__getitem__