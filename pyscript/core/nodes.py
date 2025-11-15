from .bases import Pys
from .constants import NTER_GENERAL, NUNR_LEFT
from .position import PysPosition
from .token import PysToken
from .utils.decorators import typechecked, immutable
from .utils.general import setimuattr

@immutable
class PysNode(Pys):

    __slots__ = ('position',)

    @typechecked
    def __init__(self, position: PysPosition) -> None:
        setimuattr(self, 'position', position)

    def __repr__(self):
        return 'Node()'

class PysNumberNode(PysNode):

    __slots__ = ('token',)

    @typechecked
    def __init__(self, token: PysToken) -> None:
        super().__init__(token.position)
        setimuattr(self, 'token', token)

    def __repr__(self):
        return f'Number(value={self.token.value!r})'

class PysStringNode(PysNode):

    __slots__ = ('token',)

    @typechecked
    def __init__(self, token: PysToken) -> None:
        super().__init__(token.position)
        setimuattr(self, 'token', token)

    def __repr__(self):
        return f'String(value={self.token.value!r})'

class PysKeywordNode(PysNode):

    __slots__ = ('token',)

    @typechecked
    def __init__(self, token: PysToken) -> None:
        super().__init__(token.position)
        setimuattr(self, 'token', token)

    def __repr__(self):
        return f'Keyword(name={self.token.value!r})'

class PysIdentifierNode(PysNode):

    __slots__ = ('token',)

    @typechecked
    def __init__(self, token: PysToken) -> None:
        super().__init__(token.position)
        setimuattr(self, 'token', token)

    def __repr__(self):
        return f'Identifier(name={self.token.value!r})'

class PysSequenceNode(PysNode):

    __slots__ = ('type', 'elements')

    @typechecked
    def __init__(
        self,
        type: int,
        elements: list[PysNode | PysToken | tuple[PysNode, PysNode]],
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'type', type)
        setimuattr(self, 'elements', tuple(elements))

    def __repr__(self):
        return f'Sequence(type={self.type!r}, elements={self.elements!r})'

class PysAttributeNode(PysNode):

    __slots__ = ('target', 'attribute')

    @typechecked
    def __init__(self, target: PysNode, attribute: PysToken) -> None:
        super().__init__(PysPosition(target.position.file, target.position.start, attribute.position.end))
        setimuattr(self, 'target', target)
        setimuattr(self, 'attribute', attribute)

    def __repr__(self):
        return f'Attribute(target={self.target!r}, attribute={self.attribute!r})'

class PysSubscriptNode(PysNode):

    __slots__ = ('target', 'slice')

    @typechecked
    def __init__(
        self,
        target: PysNode,
        slice: PysNode | slice | list[PysNode | slice],
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'slice', tuple(slice) if isinstance(slice, list) else slice)

    def __repr__(self):
        return f'Subscript(target={self.target!r}, slice={self.slice!r})'

class PysChainOperatorNode(PysNode):

    __slots__ = ('operations', 'expressions')

    @typechecked
    def __init__(self, operations: list[PysToken], expressions: list[PysNode]) -> None:
        super().__init__(
            PysPosition(
                expressions[0].position.file,
                expressions[0].position.start,
                expressions[-1].position.end
            )
        )

        setimuattr(self, 'operations', tuple(operations))
        setimuattr(self, 'expressions', tuple(expressions))

    def __repr__(self):
        return f'ChainOperator(operations={self.operations!r}, expressions={self.expressions!r})'

class PysTernaryOperatorNode(PysNode):

    __slots__ = ('condition', 'valid', 'invalid', 'style')

    @typechecked
    def __init__(self, condition: PysNode, valid: PysNode, invalid: PysNode, style: int) -> None:
        super().__init__(
            PysPosition(condition.position.file, condition.position.start, invalid.position.end)
            if style == NTER_GENERAL else
            PysPosition(condition.position.file, valid.position.start, invalid.position.end)
        )

        setimuattr(self, 'condition', condition)
        setimuattr(self, 'valid', valid)
        setimuattr(self, 'invalid', invalid)
        setimuattr(self, 'style', style)

    def __repr__(self):
        return (
            'TernaryOperator('
            f'condition={self.condition!r}, valid={self.valid!r}, invalid={self.invalid!r}, style={self.style!r})'
        )

class PysBinaryOperatorNode(PysNode):

    __slots__ = ('left', 'operand', 'right')

    @typechecked
    def __init__(self, left: PysNode, operand: PysToken, right: PysNode) -> None:
        super().__init__(PysPosition(left.position.file, left.position.start, right.position.end))
        setimuattr(self, 'left', left)
        setimuattr(self, 'operand', operand)
        setimuattr(self, 'right', right)

    def __repr__(self):
        return f'BinaryOperator(left={self.left!r}, operand={self.operand!r}, right={self.right!r})'

class PysUnaryOperatorNode(PysNode):

    __slots__ = ('operand', 'value', 'operand_position')

    @typechecked
    def __init__(self, operand: PysToken, value: PysNode, operand_position: int) -> None:
        super().__init__(
            PysPosition(operand.position.file, operand.position.start, value.position.end)
            if operand_position == NUNR_LEFT else
            PysPosition(operand.position.file, value.position.start, operand.position.end)
        )

        setimuattr(self, 'operand',  operand)
        setimuattr(self, 'value', value)
        setimuattr(self, 'operand_position', operand_position)

    def __repr__(self):
        return (
            'UnaryOperator('
            f'operand={self.operand!r}, value={self.value!r}, operand_position={self.operand_position!r})'
        )

class PysAssignNode(PysNode):

    __slots__ = ('target', 'operand', 'value')

    @typechecked
    def __init__(self, target: PysNode, operand: PysToken, value: PysNode) -> None:
        super().__init__(PysPosition(target.position.file, target.position.start, value.position.end))
        setimuattr(self, 'target', target)
        setimuattr(self, 'operand', operand)
        setimuattr(self, 'value', value)

    def __repr__(self):
        return f'Assign(target={self.target!r}, operand={self.operand!r}, value={self.value!r})'

class PysImportNode(PysNode):

    __slots__ = ('name', 'packages')

    @typechecked
    def __init__(
        self,
        name: tuple[PysToken, PysToken | None],
        packages: list[tuple[PysToken, PysToken | None]] | int,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'name', name)
        setimuattr(self, 'packages', packages if isinstance(packages, int) else tuple(packages))

    def __repr__(self):
        return f'Import(name={self.name!r}, packages={self.packages!r})'

class PysIfNode(PysNode):

    __slots__ = ('cases_body', 'else_body')

    @typechecked
    def __init__(
        self,
        cases_body: list[tuple[PysNode, PysNode]],
        else_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'cases_body', tuple(cases_body))
        setimuattr(self, 'else_body', else_body)

    def __repr__(self):
        return f'If(cases_body={self.cases_body!r}, else_body={self.else_body!r})'

class PysSwitchNode(PysNode):

    __slots__ = ('target', 'case_cases', 'default_body')

    @typechecked
    def __init__(
        self,
        target: PysNode,
        case_cases: list[tuple[PysNode, PysNode]],
        default_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'case_cases', tuple(case_cases))
        setimuattr(self, 'default_body', default_body)

    def __repr__(self):
        return f'Switch(target={self.target!r}, case_cases={self.case_cases!r}, default_body={self.default_body!r})'

class PysTryNode(PysNode):

    __slots__ = ('body', 'catch_cases', 'else_body', 'finally_body')

    @typechecked
    def __init__(
        self,
        body: PysNode,
        catch_cases: list[tuple[tuple[PysIdentifierNode | None, PysToken | None], PysNode]],
        else_body: PysNode | None,
        finally_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'body', body)
        setimuattr(self, 'catch_cases', tuple(catch_cases))
        setimuattr(self, 'else_body', else_body)
        setimuattr(self, 'finally_body', finally_body)

    def __repr__(self):
        return (
            'Try('
                f'body={self.body!r}, '
                f'catch_cases={self.catch_cases!r}, '
                f'else_body={self.else_body!r}, '
                f'finally_body={self.finally_body!r}'
            ')'
        )

class PysWithNode(PysNode):

    __slots__ = ('context', 'alias', 'body')

    @typechecked
    def __init__(self, context: PysNode, alias: PysToken | None, body: PysNode, position: PysPosition) -> None:
        super().__init__(position)
        setimuattr(self, 'context', context)
        setimuattr(self, 'alias', alias)
        setimuattr(self, 'body', body)

    def __repr__(self):
        return f'With(context={self.context!r}, alias={self.alias!r}, body={self.body!r})'

class PysForNode(PysNode):

    __slots__ = ('header', 'body', 'else_body')

    @typechecked
    def __init__(
        self,
        header: tuple[PysNode | None, PysNode | None, PysNode | None] |
                tuple[PysNode, PysNode],
        body: PysNode | None,
        else_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'header', header)
        setimuattr(self, 'body', body)
        setimuattr(self, 'else_body', else_body)

    def __repr__(self):
        return f'For(header={self.header!r}, body={self.body!r}, else_body={self.else_body!r})'

class PysWhileNode(PysNode):

    __slots__ = ('condition', 'body', 'else_body')

    @typechecked
    def __init__(
        self,
        condition: PysNode,
        body: PysNode | None,
        else_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'body', body)
        setimuattr(self, 'else_body', else_body)

    def __repr__(self):
        return f'While(condition={self.condition!r}, body={self.body!r}, else_body={self.else_body!r})'

class PysDoWhileNode(PysNode):

    __slots__ = ('body', 'condition', 'else_body')

    @typechecked
    def __init__(
        self,
        body: PysNode | None,
        condition: PysNode,
        else_body: PysNode | None,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'body', body)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'else_body', else_body)

    def __repr__(self):
        return f'DoWhile(body={self.body!r}, condition={self.condition!r}, else_body={self.else_body!r})'

class PysClassNode(PysNode):

    __slots__ = ('decorators', 'name', 'bases', 'body')

    @typechecked
    def __init__(
        self,
        decorators: list[PysNode],
        name: PysToken,
        bases: list[PysNode],
        body: PysNode,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'decorators', tuple(decorators))
        setimuattr(self, 'name', name)
        setimuattr(self, 'bases', tuple(bases))
        setimuattr(self, 'body', body)

    def __repr__(self):
        return f'Class(decorators={self.decorators!r}, name={self.name!r}, bases={self.bases!r}, body={self.body!r})'

class PysFunctionNode(PysNode):

    __slots__ = ('decorators', 'name', 'parameters', 'body')

    @typechecked
    def __init__(
        self,
        decorators: list[PysNode],
        name: PysToken | None,
        parameters: list[PysToken | tuple[PysToken, PysNode]],
        body: PysNode,
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'decorators', tuple(decorators))
        setimuattr(self, 'name', name)
        setimuattr(self, 'parameters', tuple(parameters))
        setimuattr(self, 'body', body)

    def __repr__(self):
        return (
            'Function('
            f'decorators={self.decorators!r}, name={self.name!r}, parameters={self.parameters!r}, body={self.body!r})'
        )

class PysCallNode(PysNode):

    __slots__ = ('target', 'arguments')

    @typechecked
    def __init__(
        self,
        target: PysNode,
        arguments: list[PysNode | tuple[PysToken, PysNode]],
        position: PysPosition
    ) -> None:

        super().__init__(position)
        setimuattr(self, 'target', target)
        setimuattr(self, 'arguments', tuple(arguments))

    def __repr__(self):
        return f'Call(target={self.target!r}, arguments={self.arguments!r})'

class PysReturnNode(PysNode):

    __slots__ = ('value',)

    @typechecked
    def __init__(self, value: PysNode | None, position: PysPosition) -> None:
        super().__init__(position)
        setimuattr(self, 'value', value)

    def __repr__(self):
        return f'Return(value={self.value!r})'

class PysThrowNode(PysNode):

    __slots__ = ('target',)

    @typechecked
    def __init__(self, target: PysNode, position: PysPosition) -> None:
        super().__init__(PysPosition(position.file, position.start, target.position.end))
        setimuattr(self, 'target', target)

    def __repr__(self):
        return f'Throw(target={self.target!r})'

class PysAssertNode(PysNode):

    __slots__ = ('condition', 'message')

    @typechecked
    def __init__(self, condition: PysNode, message: PysNode | None) -> None:
        super().__init__(condition.position)
        setimuattr(self, 'condition', condition)
        setimuattr(self, 'message', message)

    def __repr__(self):
        return f'Assert(condition={self.condition!r}, message={self.message!r})'

class PysEllipsisNode(PysNode):

    __slots__ = ()

    def __repr__(self):
        return 'Ellipsis()'

class PysContinueNode(PysNode):

    __slots__ = ()

    def __repr__(self):
        return 'Continue()'

class PysBreakNode(PysNode):

    __slots__ = ()

    def __repr__(self):
        return 'Break()'