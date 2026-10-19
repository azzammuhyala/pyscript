from .bases import Pys
from .cache import undefined, intern_object, PysUndefined
from .mapping import GET_BINARY_FUNCTION, GET_UNARY_FUNCTION
from .position import PysPosition
from .token import TOKENS, PysToken
from .utils.decorators import typecheck, immutable, inheritable
from .utils.generic import setimuattr

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    # circular import problem solved
    from .pystypes import jsdict

@immutable
class PysNode(Pys):

    __slots__ = ('position',)

    @typecheck
    def __new__(cls, position: PysPosition):
        self = super().__new__(cls)
        setimuattr(self, 'position', position)
        return self

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        inheritable(cls)

    def __repr__(self) -> Literal['Node()']:
        return 'Node()'

class PysConstantNode(PysNode):

    __slots__ = ('value',)

    @typecheck
    def __new__(cls, position: PysPosition, value: Any | PysNode) -> 'PysConstantNode | PysNode':
        if isinstance(value, PysNode):
            return value

        self = super().__new__(cls, position)
        setimuattr(self, 'value', intern_object(value))
        return self

    def __repr__(self) -> str:
        return f'Constant(value={self.value!r})'

class PysDebugNode(PysNode):

    __slots__ = ()

    def __repr__(self) -> Literal['Debug()']:
        return 'Debug()'

class PysIdentifierNode(PysNode):

    __slots__ = ('name',)

    @typecheck
    def __new__(cls, name: PysToken) -> 'PysIdentifierNode':
        self = super().__new__(cls, name.position)
        setimuattr(self, 'name', name)
        return self

    def __repr__(self) -> str:
        return f'Identifier(name={self.name!r})'

class PysDictionaryNode(PysNode):

    __slots__ = ('pairs', 'class_type')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        pairs: list[tuple[PysNode, PysNode]],
        class_type: type[dict] | type['jsdict']
    ) -> 'PysDictionaryNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'pairs', tuple(pairs))
        setimuattr(self, 'class_type', class_type)
        return self

    def __repr__(self) -> str:
        return f'Dictionary(pairs={self.pairs!r}, class_type={self.class_type.__name__})'

class PysSetNode(PysNode):

    __slots__ = ('elements',)

    @typecheck
    def __new__(cls, position: PysPosition, elements: list[PysNode]) -> 'PysSetNode':
        self = super().__new__(cls, position)
        setimuattr(self, 'elements', tuple(elements))
        return self

    def __repr__(self) -> str:
        return f'Set(elements={self.elements!r})'

class PysListNode(PysNode):

    __slots__ = ('elements',)

    @typecheck
    def __new__(cls, position: PysPosition, elements: list[PysNode]) -> 'PysListNode':
        self = super().__new__(cls, position)
        setimuattr(self, 'elements', tuple(elements))
        return self

    def __repr__(self) -> str:
        return f'List(elements={self.elements!r})'

class PysTupleNode(PysNode):

    __slots__ = ('elements',)

    @typecheck
    def __new__(cls, position: PysPosition, elements: list[PysNode]) -> 'PysTupleNode | PysConstantNode':
        if (l_elements := _get_literal_value(elements)) is not undefined:
            return PysConstantNode(position, l_elements)

        self = super().__new__(cls, position)
        setimuattr(self, 'elements', tuple(elements))
        return self

    def __repr__(self) -> str:
        return f'Tuple(elements={self.elements!r})'

class PysAttributeNode(PysNode):

    __slots__ = ('target', 'attribute')

    @typecheck
    def __new__(cls, target: PysNode, attribute: PysToken) -> 'PysAttributeNode':
        self = super().__new__(cls, PysPosition(target.position.file, target.position.start, attribute.position.end))
        setimuattr(self, 'target', target)
        setimuattr(self, 'attribute', attribute)
        return self

    def __repr__(self) -> str:
        return f'Attribute(target={self.target!r}, attribute={self.attribute!r})'

class PysSubscriptNode(PysNode):

    __slots__ = ('target', 'slice')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        target: PysNode,
        slice: PysNode | slice | list[PysNode | slice]
    ) -> 'PysSubscriptNode | PysConstantNode':
        if (
            (l_target := _get_literal_value(target)) is not undefined and
            (l_slice := _get_literal_value(slice)) is not undefined
        ):
            try:
                return PysConstantNode(position, l_target[l_slice])
            except:
                pass

        self = super().__new__(cls, position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'slice', tuple(slice) if isinstance(slice, list) else slice)
        return self

    def __repr__(self) -> str:
        return f'Subscript(target={self.target!r}, slice={self.slice!r})'

class PysCallNode(PysNode):

    __slots__ = ('target', 'arguments')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        target: PysNode,
        arguments: list[PysNode | tuple[PysToken, PysNode]]
    ) -> 'PysCallNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'arguments', tuple(arguments))
        return self

    def __repr__(self) -> str:
        return f'Call(target={self.target!r}, arguments={self.arguments!r})'

class PysChainOperatorNode(PysNode):

    __slots__ = ('operations', 'expressions')

    @typecheck
    def __new__(
        cls,
        operations: list[PysToken],
        expressions: list[PysNode]
    ) -> 'PysChainOperatorNode | PysConstantNode':
        # circular import problem solved
        from .pysbuiltins import ce, nce

        def fold(i):
            left, right = _get_literal_value(expressions[i]), _get_literal_value(expressions[i + 1])
            if left is undefined or right is undefined:
                return undefined
            try:
                type = operations[i].type
                if type == TOKENS['EQUAL_TILDE']:
                    return ce(left, right)
                elif type == TOKENS['EXCLAMATION_TILDE']:
                    return nce(left, right)
                return GET_BINARY_FUNCTION(type)(left, right)
            except:
                return undefined

        total_operations = len(operations)
        start = 0
        end = total_operations

        while start < total_operations:
            result = fold(start)
            if result is undefined:
                break
            if not result or start == total_operations - 1:
                return PysConstantNode(
                    PysPosition(
                        expressions[0].position.file,
                        expressions[0].position.start,
                        expressions[-1].position.end
                    ),
                    result
                )
            start += 1

        for i in range(start, end):
            result = fold(i)
            if result is not undefined and not result:
                end = i + 1
                break

        if start != 0 or end != total_operations:
            operations = operations[start:end]
            expressions = expressions[start:end + 1]

        self = super().__new__(
            cls,
            PysPosition(
                expressions[0].position.file,
                expressions[0].position.start,
                expressions[-1].position.end
            )
        )

        setimuattr(self, 'operations', tuple(operations))
        setimuattr(self, 'expressions', tuple(expressions))
        return self

    def __repr__(self) -> str:
        return f'ChainOperator(operations={self.operations!r}, expressions={self.expressions!r})'

class PysTernaryOperatorNode(PysNode):

    __slots__ = ('condition', 'valid', 'invalid', 'style')

    @typecheck
    def __new__(
        cls,
        condition: PysNode,
        valid: PysNode,
        invalid: PysNode,
        style: Literal['general', 'pythonic']
    ) -> 'PysTernaryOperatorNode | PysNode':
        if (l_condition := _get_literal_value(condition)) is not undefined:
            return valid if l_condition else invalid

        self = super().__new__(
            cls,
            PysPosition(condition.position.file, condition.position.start, invalid.position.end)
            if style == 'general' else
            PysPosition(condition.position.file, valid.position.start, invalid.position.end)
        )

        setimuattr(self, 'condition', condition)
        setimuattr(self, 'valid', valid)
        setimuattr(self, 'invalid', invalid)
        setimuattr(self, 'style', style)
        return self

    def __repr__(self) -> str:
        return (
            'TernaryOperator('
                f'condition={self.condition!r}, '
                f'valid={self.valid!r}, '
                f'invalid={self.invalid!r}, '
                f'style={self.style!r}'
            ')'
        )

class PysBinaryOperatorNode(PysNode):

    __slots__ = ('left', 'operand', 'right')

    @typecheck
    def __new__(
        cls,
        left: PysNode,
        operand: PysToken,
        right: PysNode
    ) -> 'PysBinaryOperatorNode | PysNode':
        position = PysPosition(left.position.file, left.position.start, right.position.end)

        if (l_left := _get_literal_value(left)) is not undefined:
            if operand.type == (TOKENS['DOUBLE_PIPE'] if l_left else TOKENS['DOUBLE_AMPERSAND']):
                return PysConstantNode(left.position, l_left)
            elif l_left is None and operand.type == TOKENS['DOUBLE_QUESTION']:
                return right
            elif (l_right := _get_literal_value(right)) is not undefined:
                try:
                    return PysConstantNode(position, GET_BINARY_FUNCTION(operand.type)(l_left, l_right))
                except:
                    pass

        self = super().__new__(cls, position)
        setimuattr(self, 'left', left)
        setimuattr(self, 'operand', operand)
        setimuattr(self, 'right', right)
        return self

    def __repr__(self) -> str:
        return f'BinaryOperator(left={self.left!r}, operand={self.operand!r}, right={self.right!r})'

class PysUnaryOperatorNode(PysNode):

    __slots__ = ('operand', 'value')

    @typecheck
    def __new__(cls, operand: PysToken, value: PysNode) -> 'PysUnaryOperatorNode | PysConstantNode':
        position = PysPosition(operand.position.file, operand.position.start, value.position.end)

        if (l_value := _get_literal_value(value)) is not undefined:
            try:
                return PysConstantNode(position, GET_UNARY_FUNCTION(operand.type)(l_value))
            except:
                pass

        self = super().__new__(cls, position)
        setimuattr(self, 'operand', operand)
        setimuattr(self, 'value', value)
        return self

    def __repr__(self) -> str:
        return f'UnaryOperator(operand={self.operand!r}, value={self.value!r})'

class PysIncrementalNode(PysNode):

    __slots__ = ('operand', 'target', 'operand_alignment')

    @typecheck
    def __new__(
        cls,
        operand: PysToken,
        target: PysNode,
        operand_alignment: Literal['left', 'right']
    ) -> 'PysIncrementalNode':

        self = super().__new__(
            cls,
            PysPosition(operand.position.file, operand.position.start, target.position.end)
            if operand_alignment == 'left' else
            PysPosition(operand.position.file, target.position.start, operand.position.end)
        )

        setimuattr(self, 'operand', operand)
        setimuattr(self, 'target', target)
        setimuattr(self, 'operand_alignment', operand_alignment)
        return self

    def __repr__(self) -> str:
        return (
            'Incremental('
                f'operand={self.operand!r}, '
                f'target={self.target!r}, '
                f'operand_alignment={self.operand_alignment!r}'
            ')'
        )

class PysStatementsNode(PysNode):

    __slots__ = ('elements',)

    @typecheck
    def __new__(cls, position: PysPosition, elements: list[PysNode]) -> 'PysStatementsNode | PysNode':
        if len(elements) == 1:
            return elements[0]

        new = []
        constant_nodes = (PysConstantNode, PysDebugNode, PysEllipsisNode)
        interrupt_nodes = (PysReturnNode, PysThrowNode, PysContinueNode, PysBreakNode)

        for node in elements:
            if node.__class__ in constant_nodes:
                continue
            elif node.__class__ is PysStatementsNode:
                new.extend(node.elements)
            else:
                new.append(node)
            if node.__class__ in interrupt_nodes:
                break

        self = super().__new__(cls, position)
        setimuattr(self, 'elements', tuple(new))
        return self

    def __repr__(self) -> str:
        return f'Statements(elements={self.elements!r})'

class PysAssignmentNode(PysNode):

    __slots__ = ('target', 'operand', 'value')

    @typecheck
    def __new__(cls, target: PysNode, operand: PysToken, value: PysNode) -> 'PysAssignmentNode':
        self = super().__new__(cls, PysPosition(target.position.file, target.position.start, value.position.end))
        setimuattr(self, 'target', target)
        setimuattr(self, 'operand', operand)
        setimuattr(self, 'value', value)
        return self

    def __repr__(self) -> str:
        return f'Assignment(target={self.target!r}, operand={self.operand!r}, value={self.value!r})'

class PysImportNode(PysNode):

    __slots__ = ('name', 'packages')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        name: tuple[PysToken, PysToken | None],
        packages: list[tuple[PysToken, PysToken | None]] | Literal['all']
    ) -> 'PysImportNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'name', name)
        setimuattr(self, 'packages', tuple(packages) if isinstance(packages, list) else packages)
        return self

    def __repr__(self) -> str:
        return f'Import(name={self.name!r}, packages={self.packages!r})'

class PysIfNode(PysNode):

    __slots__ = ('cases', 'else_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        cases: list[tuple[PysNode, PysNode]],
        else_: PysNode | None
    ) -> 'PysIfNode | PysNode':
        new_cases = []

        for condition, body in cases:
            if (value := _get_literal_value(condition)) is undefined:
                new_cases.append((condition, body))
            elif value:
                else_ = body
                break

        else_ = _optional_part(else_)

        if not new_cases:
            return else_ if else_ else PysStatementsNode(position, [])

        elif len(new_cases) == 1:
            condition, body = new_cases[0]
            if body.__class__ is PysIfNode and len(body.cases) == 1 and body.else_:
                inner_condition, inner_body = body.cases[0]
                new_cases = [(
                    PysBinaryOperatorNode(
                        condition,
                        PysToken(TOKENS['DOUBLE_AMPERSAND'], body.position),
                        inner_condition
                    ),
                    inner_body
                )]

        self = super().__new__(cls, position)
        setimuattr(self, 'cases', tuple(new_cases))
        setimuattr(self, 'else_', else_)
        return self

    def __repr__(self) -> str:
        return f'If(cases={self.cases!r}, else_={self.else_!r})'

class PysSwitchNode(PysNode):

    __slots__ = ('target', 'cases', 'default')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        target: PysNode,
        cases: list[tuple[PysNode, PysNode]],
        default: PysNode | None
    ) -> 'PysSwitchNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'cases', tuple(cases))
        setimuattr(self, 'default', _optional_part(default))
        return self

    def __repr__(self) -> str:
        return f'Switch(target={self.target!r}, cases={self.cases!r}, default={self.default!r})'

class PysMatchNode(PysNode):

    __slots__ = ('target', 'cases', 'default')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        target: PysNode | None,
        cases: list[tuple[PysNode, PysNode]],
        default: PysNode | None
    ) -> 'PysMatchNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'cases', tuple(cases))
        setimuattr(self, 'default', _optional_part(default))
        return self

    def __repr__(self) -> str:
        return f'Match(target={self.target!r}, cases={self.cases!r}, default={self.default!r})'

class PysTryNode(PysNode):

    __slots__ = ('body', 'catches', 'else_', 'finally_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        body: PysNode,
        catches: list[tuple[tuple[tuple[PysIdentifierNode, ...], PysToken | None], PysNode]],
        else_: PysNode | None,
        finally_: PysNode | None
    ) -> 'PysTryNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'body', body)
        setimuattr(self, 'catches', tuple(catches))
        setimuattr(self, 'else_', _optional_part(else_))
        setimuattr(self, 'finally_', _optional_part(finally_))
        return self

    def __repr__(self) -> str:
        return (
            'Try('
                f'body={self.body!r}, '
                f'catches={self.catches!r}, '
                f'else_={self.else_!r}, '
                f'finally_={self.finally_!r}'
            ')'
        )

class PysWithNode(PysNode):

    __slots__ = ('contexts', 'body')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        contexts: list[tuple[PysNode, PysToken | None]],
        body: PysNode
    ) -> 'PysWithNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'contexts', tuple(contexts))
        setimuattr(self, 'body', body)
        return self

    def __repr__(self) -> str:
        return f'With(contexts={self.contexts!r}, body={self.body!r})'

class PysForNode(PysNode):

    __slots__ = ('header', 'body', 'else_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        header: tuple[PysNode | None, PysNode | None, PysNode | None] |
                tuple[PysNode, PysNode],
        body: PysNode,
        else_: PysNode | None
    ) -> 'PysForNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'header', header)
        setimuattr(self, 'body', body)
        setimuattr(self, 'else_', _optional_part(else_))
        return self

    def __repr__(self) -> str:
        return f'For(header={self.header!r}, body={self.body!r}, else_={self.else_!r})'

class PysWhileNode(PysNode):

    __slots__ = ('condition', 'body', 'else_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        condition: PysNode,
        body: PysNode,
        else_: PysNode | None
    ) -> 'PysWhileNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'body', body)
        setimuattr(self, 'else_', _optional_part(else_))
        return self

    def __repr__(self) -> str:
        return f'While(condition={self.condition!r}, body={self.body!r}, else_={self.else_!r})'

class PysDoWhileNode(PysNode):

    __slots__ = ('body', 'condition', 'else_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        body: PysNode,
        condition: PysNode,
        else_: PysNode | None
    ) -> 'PysDoWhileNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'body', body)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'else_', _optional_part(else_))
        return self

    def __repr__(self) -> str:
        return f'DoWhile(body={self.body!r}, condition={self.condition!r}, else_={self.else_!r})'

class PysRepeatNode(PysNode):

    __slots__ = ('body', 'condition', 'else_')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        body: PysNode | None,
        condition: PysNode,
        else_: PysNode | None
    ) -> 'PysRepeatNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'body', _optional_part(body))
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'else_', _optional_part(else_))
        return self

    def __repr__(self) -> str:
        return f'Repeat(body={self.body!r}, condition={self.condition!r}, else_={self.else_!r})'

class PysClassNode(PysNode):

    __slots__ = ('decorators', 'name', 'bases', 'body')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        decorators: list[PysNode],
        name: PysToken,
        bases: list[PysNode],
        body: PysNode
    ) -> 'PysClassNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'decorators', tuple(decorators))
        setimuattr(self, 'name', name)
        setimuattr(self, 'bases', tuple(bases))
        setimuattr(self, 'body', body)
        return self

    def __repr__(self) -> str:
        return f'Class(decorators={self.decorators!r}, name={self.name!r}, bases={self.bases!r}, body={self.body!r})'

class PysFunctionNode(PysNode):

    __slots__ = ('decorators', 'name', 'parameters', 'body', 'constructor')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        decorators: list[PysNode],
        name: PysToken | None,
        parameters: list[PysToken | tuple[PysToken, PysNode]],
        body: PysNode,
        constructor: bool
    ) -> 'PysFunctionNode':

        self = super().__new__(cls, position)
        setimuattr(self, 'decorators', tuple(decorators))
        setimuattr(self, 'name', name)
        setimuattr(self, 'parameters', tuple(parameters))
        setimuattr(self, 'body', body)
        setimuattr(self, 'constructor', bool(constructor))
        return self

    def __repr__(self) -> str:
        return (
            'Function('
                f'decorators={self.decorators!r}, '
                f'name={self.name!r}, '
                f'parameters={self.parameters!r}, '
                f'body={self.body!r}, '
                f'constructor={self.constructor!r}'
            ')'
        )

class PysGlobalNode(PysNode):

    __slots__ = ('identifiers',)

    @typecheck
    def __new__(cls, position: PysPosition, identifiers: list[PysToken]) -> 'PysGlobalNode':
        self = super().__new__(cls, position)
        setimuattr(self, 'identifiers', tuple(set(identifiers)))
        return self

    def __repr__(self) -> str:
        return f'Global(identifiers={self.identifiers!r})'

class PysReturnNode(PysNode):

    __slots__ = ('value',)

    @typecheck
    def __new__(cls, position: PysPosition, value: PysNode | None) -> 'PysReturnNode':
        self = super().__new__(cls, position)
        setimuattr(self, 'value', _optional_part(value))
        return self

    def __repr__(self) -> str:
        return f'Return(value={self.value!r})'

class PysThrowNode(PysNode):

    __slots__ = ('target', 'primary')

    @typecheck
    def __new__(cls, position: PysPosition, target: PysNode, primary: PysNode | None) -> 'PysThrowNode':
        self = super().__new__(
            cls,
            PysPosition(
                position.file,
                position.start,
                primary.position.end if primary else target.position.end
            )
        )

        setimuattr(self, 'target', target)
        setimuattr(self, 'primary', primary)
        return self

    def __repr__(self) -> str:
        return f'Throw(target={self.target!r}, primary={self.primary!r})'

class PysAssertNode(PysNode):

    __slots__ = ('condition', 'message')

    @typecheck
    def __new__(
        cls,
        position: PysPosition,
        condition: PysNode,
        message: PysNode | None
    ) -> 'PysAssertNode | PysStatementsNode':

        if (l_condition := _get_literal_value(condition)) is not undefined and l_condition:
            return PysStatementsNode(position, [])

        self = super().__new__(cls, position)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'message', message)
        return self

    def __repr__(self) -> str:
        return f'Assert(condition={self.condition!r}, message={self.message!r})'

class PysDeleteNode(PysNode):

    __slots__ = ('targets',)

    @typecheck
    def __new__(cls, position: PysPosition, targets: list[PysNode]) -> 'PysDeleteNode':
        self = super().__new__(cls, position)
        setimuattr(self, 'targets', tuple(targets))
        return self

    def __repr__(self) -> str:
        return f'Delete(targets={self.targets!r})'

class PysEllipsisNode(PysNode):

    __slots__ = ()

    def __repr__(self) -> Literal['Ellipsis()']:
        return 'Ellipsis()'

class PysContinueNode(PysNode):

    __slots__ = ()

    def __repr__(self) -> Literal['Continue()']:
        return 'Continue()'

class PysBreakNode(PysNode):

    __slots__ = ()

    def __repr__(self) -> Literal['Break()']:
        return 'Break()'

def _get_literal_value(item: Any) -> Any | PysUndefined:

    if isinstance(item, (PysConstantNode, PysToken)):
        return item.value

    elif isinstance(item, slice):
        start = _get_literal_value(item.start)
        if start is undefined:
            return undefined
        stop = _get_literal_value(item.stop)
        if stop is undefined:
            return undefined
        step = _get_literal_value(item.step)
        if step is undefined:
            return undefined
        return slice(start, stop, step)

    elif isinstance(item, (list, tuple)):
        constants = []
        for element in item:
            value = _get_literal_value(element)
            if value is undefined:
                return undefined
            constants.append(value)
        return tuple(constants)

    elif item is None:
        return None

    return undefined

def _optional_part(part: PysNode | None) -> PysNode | None:
    return None if (
        _get_literal_value(part) is None or
        (part.__class__ is PysStatementsNode and not part.elements) or
        (part.__class__ in (PysDebugNode, PysEllipsisNode))
    ) else part