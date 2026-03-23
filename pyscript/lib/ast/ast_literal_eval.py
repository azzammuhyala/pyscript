from pyscript.core.constants import TOKENS
from pyscript.core.interpreter import get_value_from_keyword
from pyscript.core.mapping import GET_BINARY_FUNCTIONS_MAP, GET_UNARY_FUNCTIONS_MAP, REVERSE_TOKENS
from pyscript.core.nodes import (
    PysNode, PysNumberNode, PysStringNode, PysKeywordNode, PysIdentifierNode, PysDictionaryNode, PysSetNode,
    PysListNode, PysTupleNode, PysCallNode, PysUnaryOperatorNode, PysBinaryOperatorNode, PysEllipsisNode
)
from pyscript.core.pysbuiltins import pys_builtins

from types import EllipsisType
from typing import Any, Callable

is_arithmetic = frozenset([TOKENS['PLUS'], TOKENS['MINUS']]).__contains__

inf = pys_builtins.inf
nan = pys_builtins.nan

get_identifier = {
    'ellipsis': Ellipsis,
    'Ellipsis': Ellipsis,
    'inf': inf,
    'infinity': inf,
    'Infinity': inf,
    'nan': nan,
    'notanumber': nan,
    'NaN': nan,
    'NotANumber': nan
}.get

def visit(node: PysNode) -> Any:
    return get_visitor(node.__class__)(node)

def visit_unknown_node(node: PysNode) -> None:
    raise ValueError(f"invalid node: {type(node).__name__}")

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
        raise ValueError(f"invalid identifier: {name}")
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
    raise ValueError("invalid call node except for 'set()'")

def visit_UnaryOperatorNode(node: PysUnaryOperatorNode) -> Any:
    operand = node.operand.type
    if is_arithmetic(operand):
        return GET_UNARY_FUNCTIONS_MAP(operand)(visit(node.value))
    raise ValueError(f"invalid unary operator node: {REVERSE_TOKENS[operand]}")

def visit_BinaryOperatorNode(node: PysBinaryOperatorNode) -> Any:
    operand = node.operand.type
    if is_arithmetic(operand):
        return GET_BINARY_FUNCTIONS_MAP(operand)(visit(node.left), visit(node.right))
    raise ValueError(f"invalid binary operator node: {REVERSE_TOKENS[operand]}")

def visit_EllipsisNode(node: PysEllipsisNode) -> EllipsisType:
    return ...

get_visitor: Callable[[type[PysNode]], Callable[[PysNode], Any]] = {
    class_node: globals().get('visit_' + class_node.__name__.removeprefix('Pys'), visit_unknown_node)
    for class_node in PysNode.__subclasses__()
}.__getitem__