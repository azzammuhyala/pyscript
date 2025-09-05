from .bases import Pys
from .position import PysPositionRange

class PysNode(Pys):
    pass

class PysNumberNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'Number({!r})'.format(self.token.value)

class PysStringNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'String({!r})'.format(self.token.value)

class PysSequenceNode(PysNode):

    def __init__(self, type, elements, position):
        self.position = position
        self.type = type
        self.elements = elements

    def __repr__(self):
        return 'Sequence({!r}, {!r})'.format(self.type, self.elements)

class PysSubscriptNode(PysNode):

    def __init__(self, object, slice, position):
        self.position = position
        self.object = object
        self.slice = slice

    def __repr__(self):
        return 'Subscript({!r}, {!r})'.format(self.object, self.slice)

class PysAccessNode(PysNode):

    def __init__(self, name, protected=False):
        self.position = name.position
        self.name = name
        self.protected = protected

    def __repr__(self):
        return 'Access({!r})'.format(self.name.value)

class PysAttributeNode(PysNode):

    def __init__(self, object, attribute):
        self.position = PysPositionRange(object.position.start, attribute.position.end)
        self.object = object
        self.attribute = attribute

    def __repr__(self):
        return 'Attribute({!r}, {!r})'.format(self.object, self.attribute)

class PysAssignNode(PysNode):

    def __init__(self, variable, operand, value):
        self.position = PysPositionRange(variable.position.start, value.position.end)
        self.variable = variable
        self.operand = operand
        self.value = value

    def __repr__(self):
        return 'Assign({!r}, {!r}, {!r})'.format(self.variable, self.operand, self.value)

class PysChainOperatorNode(PysNode):

    def __init__(self, operations, expressions):
        self.position = PysPositionRange(expressions[0].position.start, expressions[-1].position.end)
        self.operations = operations
        self.expressions = expressions

    def __repr__(self):
        return 'ChainOperator({!r}, {!r})'.format(self.operations, self.expressions)

class PysBinaryOperatorNode(PysNode):

    def __init__(self, left, operand, right):
        self.position = PysPositionRange(left.position.start, right.position.end)
        self.left = left
        self.operand = operand
        self.right = right

    def __repr__(self):
        return 'BinaryOperator({!r}, {!r}, {!r})'.format(self.left, self.operand, self.right)

class PysUnaryOperatorNode(PysNode):

    def __init__(self, operand, value, operand_position='left'):
        self.position = (
            PysPositionRange(operand.position.start, value.position.end)
            if operand_position == 'left' else
            PysPositionRange(value.position.start, operand.position.end)
        )

        self.operand = operand
        self.value = value
        self.operand_position = operand_position

    def __repr__(self):
        return (
            'UnaryOperator({!r}, {!r})'.format(self.operand, self.value)
            if self.operand_position == 'left' else
            'UnaryOperator({!r}, {!r})'.format(self.value, self.operand)
        )

class PysTernaryOperatorNode(PysNode):

    def __init__(self, condition, valid, invalid):
        self.position = PysPositionRange(condition.position.start, invalid.position.end)
        self.condition = condition
        self.valid = valid
        self.invalid = invalid

    def __repr__(self):
        return 'TernaryOperator({!r}, {!r}, {!r})'.format(self.condition, self.valid, self.invalid)

class PysIfNode(PysNode):

    def __init__(self, cases, else_case):
        self.position = PysPositionRange(cases[0][0].position.start, (else_case or cases[-1][1]).position.end)
        self.cases = cases
        self.else_case = else_case

    def __repr__(self):
        return 'If({!r}, {!r})'.format(self.cases, self.else_case)

class PysSwitchNode(PysNode):

    def __init__(self, expression, cases, default_case):
        self.position = PysPositionRange(
            expression.position.start,
            (
                default_case or
                (cases[-1][1] if cases else expression)
            ).position.end
        )

        self.expression = expression
        self.cases = cases
        self.default_case = default_case

    def __repr__(self):
        return 'Switch({!r}, {!r}, {!r})'.format(self.expression, self.cases, self.default_case)

class PysTryNode(PysNode):

    def __init__(self, body, variable, catch):
        self.position = PysPositionRange(body.position.start, catch.position.end)
        self.body = body
        self.variable = variable
        self.catch = catch

    def __repr__(self):
        return 'Try({!r}, {!r}, {!r})'.format(self.body, self.variable, self.catch)

class PysForNode(PysNode):

    def __init__(self, iterable, body, position):
        self.position = position
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return 'For({!r}, {!r})'.format(self.iterable, self.body)

class PysWhileNode(PysNode):

    def __init__(self, condition, body):
        self.position = PysPositionRange(condition.position.start, body.position.end)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return 'While({!r}, {!r})'.format(self.condition, self.body)

class PysFunctionNode(PysNode):

    def __init__(self, name, parameter, body, position, position_parameter):
        self.position = position
        self.position_parameter = position_parameter
        self.name = name
        self.parameter = parameter
        self.body = body

    def __repr__(self):
        return 'Function({!r}, {!r}, {!r})'.format(self.name, self.parameter, self.body)

class PysCallNode(PysNode):

    def __init__(self, name, args, position):
        self.position = position
        self.name = name
        self.args = args

    def __repr__(self):
        return 'Call({!r}, {!r})'.format(self.name, self.args)

class PysReturnNode(PysNode):

    def __init__(self, expression, position):
        self.position = position
        self.expression = expression

    def __repr__(self):
        return 'Return({})'.format(repr(self.expression) if self.expression else "")

class PysThrowNode(PysNode):

    def __init__(self, node, position):
        self.position = position
        self.node = node

    def __repr__(self):
        return 'Throw({!r})'.format(self.node)

class PysContinueNode(PysNode):

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Continue()'

class PysBreakNode(PysNode):

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Break()'

class PysDeleteNode(PysNode):

    def __init__(self, objects):
        self.position = PysPositionRange(objects[0].position.start, objects[-1].position.end)
        self.objects = objects

    def __repr__(self):
        return 'Delete({!r})'.format(self.objects)