from .bases import Pys
from .exceptions import PysException
from .values import PysShouldReturn, PysFunction, PysMethod
from .constants import TOKENS
from .utils import SYNTAX, is_exception, Iterable
from .pysbuiltins import closeeq
from .singletons import undefined
from .nodes import *

class PysRunTimeResult(Pys):

    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, result):
        self.error = result.error
        self.func_return_value = result.func_return_value
        self.loop_should_continue = result.loop_should_continue
        self.loop_should_break = result.loop_should_break

        return result.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error or
            self.func_return_value or
            self.loop_should_continue or
            self.loop_should_break
        )

def visit_slice_from_SubscriptNode(self, result, slice_node, context):
    if isinstance(slice_node, tuple):
        start, stop, step = slice_node

        if start is not None:
            start = result.register(self.visit(start, context))
            if result.should_return():
                return result

        if stop is not None:
            stop = result.register(self.visit(stop, context))
            if result.should_return():
                return result

        if step is not None:
            step = result.register(self.visit(step, context))
            if result.should_return():
                return result

        return slice(start, stop, step)

    elif isinstance(slice_node, list):
        slice_node = []

        for element in slice_node:
            slice_node.append(visit_slice_from_SubscriptNode(self, result, element, context))
            if result.should_return():
                return result

        return tuple(slice_node)

    else:
        value = result.register(self.visit(slice_node, context))
        if result.should_return():
            return result

        return value

def unpack_assign(self, result, node, value, context, operand=TOKENS['EQ']):

    if isinstance(node, PysSequenceNode):

        if not isinstance(value, Iterable):
            return result.failure(
                PysException(
                    TypeError("cannot unpack non-iterable"),
                    node.position,
                    context
                )
            )

        count = 0

        for i, element in enumerate(value):

            if i < len(node.elements):
                unpack_assign(self, result, node.elements[i], element, context, operand)
                if result.should_return():
                    return result

                count += 1

            else:
                return result.failure(
                    PysException(
                        ValueError("to many values to unpack (expected {})".format(len(node.elements))),
                        node.position,
                        context
                    )
                )

        if count < len(node.elements):
            return result.failure(
                PysException(
                    ValueError("not enough values to unpack (expected {}, got {})".format(len(node.elements), count)),
                    node.position,
                    context
                )
            )

    elif isinstance(node, PysSubscriptNode):
        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        slice = visit_slice_from_SubscriptNode(self, result, node.slice, context)
        if result.should_return():
            return result

        try:
            object[slice] = value
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    elif isinstance(node, PysAttributeNode):
        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        try:
            setattr(object, node.attribute.name.value, value)
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    elif isinstance(node, PysAccessNode):
        try:
            if not context.symbol_table.set(node.name.value, value, operand):
                return result.failure(
                    PysException(
                        NameError("'{}' is not defined".format(node.name.value)),
                        node.position,
                        context
                    )
                )
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

class PysInterpreter(Pys):

    def visit(self, node, context):
        return getattr(self, 'visit_' + type(node).__name__[3:])(node, context)

    def visit_NumberNode(self, node, context):
        return PysRunTimeResult().success(node.token.value)

    def visit_StringNode(self, node, context):
        return PysRunTimeResult().success(node.token.value)

    def visit_SequenceNode(self, node, context):
        result = PysRunTimeResult()
        elements = []

        for element in node.elements:

            if isinstance(element, tuple):
                key = result.register(self.visit(element[0], context))
                if result.should_return():
                    return result

                value = result.register(self.visit(element[1], context))
                if result.should_return():
                    return result

                elements.append((key, value))

            else:
                value = result.register(self.visit(element, context))
                if result.should_return():
                    return result

                elements.append(value)

        try:
            if node.type == 'tuple':
                elements = tuple(elements)
            elif node.type == 'dict':
                elements = dict(elements)
            elif node.type == 'set':
                elements = set(elements)
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

        return result.success(elements)

    def visit_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        slice = visit_slice_from_SubscriptNode(self, result, node.slice, context)
        if result.should_return():
            return result

        try:
            return result.success(object[slice])
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    def visit_AccessNode(self, node, context):
        result = PysRunTimeResult()

        if node.name.value == 'True':
            return result.success(True)
        elif node.name.value == 'False':
            return result.success(False)
        elif node.name.value == 'None':
            return result.success(None)

        value = context.symbol_table.get(node.name.value)

        if value is undefined:
            return result.failure(
                PysException(
                    NameError("'{}' is not defined".format(node.name.value)),
                    node.position,
                    context
                )
            )

        return result.success(value)

    def visit_AttributeNode(self, node, context):
        result = PysRunTimeResult()

        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        try:
            attribute = getattr(object, node.attribute.name.value)
        except BaseException as e:
            return result.failure(PysException(e, node.attribute.position, context))

        return result.success(attribute)

    def visit_AssignNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        unpack_assign(self, result, node.variable, value, context, node.operand.type)
        if result.should_return():
            return result

        return result.success(undefined)

    def visit_ChainOperatorNode(self, node, context):
        result = PysRunTimeResult()

        left = result.register(self.visit(node.expressions[0], context))
        if result.should_return():
            return result

        try:

            for i, operand in enumerate(node.operations):
                right = result.register(self.visit(node.expressions[i + 1], context))
                if result.should_return():
                    return result

                if operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['in']):
                    comparison = left in right
                elif operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['is']):
                    comparison = left is right
                elif operand.type == TOKENS['EE']:
                    comparison = left == right
                elif operand.type == TOKENS['CE']:
                    comparison = closeeq(left, right)
                elif operand.type == TOKENS['NE']:
                    comparison = left != right
                elif operand.type == TOKENS['LT']:
                    comparison = left < right
                elif operand.type == TOKENS['GT']:
                    comparison = left > right
                elif operand.type == TOKENS['LTE']:
                    comparison = left <= right
                elif operand.type == TOKENS['GTE']:
                    comparison = left >= right

                if not comparison:
                    return result.success(False)

                left = right

        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

        return result.success(True)

    def visit_BinaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        left = result.register(self.visit(node.left, context))
        if result.should_return():
            return result

        if node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['and']):
            if left:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                return result.success(right)
            return result.success(left)

        elif node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['or']):
            if not left:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                return result.success(right)
            return result.success(left)

        else:
            right = result.register(self.visit(node.right, context))
            if result.should_return():
                return result

        try:

            if node.operand.type == TOKENS['AND']:
                return result.success(left & right)
            elif node.operand.type == TOKENS['OR']:
                return result.success(left | right)
            elif node.operand.type == TOKENS['XOR']:
                return result.success(left ^ right)
            elif node.operand.type == TOKENS['LSHIFT']:
                return result.success(left << right)
            elif node.operand.type == TOKENS['RSHIFT']:
                return result.success(left >> right)
            elif node.operand.type == TOKENS['PLUS']:
                return result.success(left + right)
            elif node.operand.type == TOKENS['MINUS']:
                return result.success(left - right)
            elif node.operand.type == TOKENS['MUL']:
                return result.success(left * right)
            elif node.operand.type == TOKENS['DIV']:
                return result.success(left / right)
            elif node.operand.type == TOKENS['FDIV']:
                return result.success(left // right)
            elif node.operand.type == TOKENS['MOD']:
                return result.success(left % right)
            elif node.operand.type == TOKENS['POW']:
                return result.success(left ** right)

        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    def visit_UnaryOperatorNode(self, node: PysUnaryOperatorNode, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        try:

            if node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['not']):
                return result.success(not value)
            elif node.operand.type == TOKENS['PLUS']:
                return result.success(+value)
            elif node.operand.type == TOKENS['MINUS']:
                return result.success(-value)
            elif node.operand.type == TOKENS['NOT']:
                return result.success(~value)

        except Exception as e:
            return result.failure(PysException(e, node.position, context))

    def visit_TernaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        condition = result.register(self.visit(node.condition, context))
        if result.should_return():
            return result

        if condition:
            value = result.register(self.visit(node.valid, context))
            if result.should_return():
                return result
        else:
            value = result.register(self.visit(node.invalid, context))
            if result.should_return():
                return result

        return result.success(value)

    def visit_IfNode(self, node, context):
        result = PysRunTimeResult()

        for condition, body in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if condition_value:
                result.register(self.visit(body, context))
                if result.should_return():
                    return result

                return result.success(undefined)

        if node.else_case:
            result.register(self.visit(node.else_case, context))
            if result.should_return():
                return result

        return result.success(undefined)

    def visit_SwitchNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.expression, context))
        if result.should_return():
            return result

        fall_through = False

        for condition, body in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if fall_through or value == condition_value:
                result.register(self.visit(body, context))
                if result.should_return() and not result.loop_should_break:
                    return result

                if result.loop_should_break:
                    result.loop_should_break = False
                    fall_through = False
                else:
                    fall_through = True

        if fall_through and node.default_case:
            result.register(self.visit(node.default_case, context))
            if result.should_return() and not result.loop_should_break:
                return result

            if result.loop_should_break:
                result.loop_should_break = False

        return result.success(undefined)

    def visit_TryNode(self, node, context):
        result = PysRunTimeResult()

        result.register(self.visit(node.body, context))

        if result.should_return():
            if node.variable:
                context.symbol_table.set(node.variable.name.value, result.error.exception)

            result.register(self.visit(node.catch, context))
            if result.should_return():
                return result

        return result.success(undefined)

    def visit_ForNode(self, node, context):
        result = PysRunTimeResult()

        if len(node.iterable) == 2:
            iterable = result.register(self.visit(node.iterable[1], context))
            if result.should_return():
                return result

            iterable = iter(iterable)

            def condition():
                try:
                    unpack_assign(self, result, node.iterable[0], next(iterable), context)
                    if result.should_return():
                        return

                except StopIteration:
                    return False

                except BaseException as e:
                    result.failure(PysException(e, node.position, context))
                    return

                return True

            def update():
                pass

        elif len(node.iterable) == 3:
            if node.iterable[0]:
                result.register(self.visit(node.iterable[0], context))
                if result.should_return():
                    return result

            def condition():
                if node.iterable[1]:
                    value = result.register(self.visit(node.iterable[1], context))
                    if result.should_return():
                        return False

                    return value

                return True

            def update():
                if node.iterable[2]:
                    result.register(self.visit(node.iterable[2], context))

        while True:
            done = condition()
            if result.should_return():
                return result

            if not done:
                break

            result.register(self.visit(node.body, context))
            if result.should_return() and not result.loop_should_continue and not result.loop_should_break:
                return result

            if result.loop_should_continue:
                result.loop_should_continue = False
                continue

            if result.loop_should_break:
                result.loop_should_break = False
                break

            update()
            if result.should_return():
                return result

        return result.success(undefined)

    def visit_WhileNode(self, node, context):
        result = PysRunTimeResult()

        while True:
            condition = result.register(self.visit(node.condition, context))
            if result.should_return():
                return result

            if not condition:
                break

            result.register(self.visit(node.body, context))
            if result.should_return() and not result.loop_should_continue and not result.loop_should_break:
                return result

            if result.loop_should_continue:
                result.loop_should_continue = False
                continue

            if result.loop_should_break:
                result.loop_should_break = False
                break

        return result.success(undefined)

    def visit_FunctionNode(self, node, context):
        result = PysRunTimeResult()

        parameter = []

        for arg in node.parameter:

            if isinstance(arg, tuple):
                value = result.register(self.visit(arg[1], context))
                if result.should_return():
                    return result

                parameter.append((arg[0].name.value, value))

            else:
                parameter.append(arg.name.value)

        func = PysFunction(
            None if node.name is None else node.name.name.value,
            parameter,
            node.body,
            node.position_parameter,
            context
        )

        if node.name is not None:
            context.symbol_table.set(func.__name__, func)

        return result.success(func)

    def visit_CallNode(self, node, context):
        result = PysRunTimeResult()

        name = result.register(self.visit(node.name, context))
        if result.should_return():
            return result

        args = []
        kwargs = {}

        for element in node.args:

            if isinstance(element, tuple):
                value = result.register(self.visit(element[1], context))
                if result.should_return():
                    return result

                kwargs[element[0].name.value] = value

            else:
                value = result.register(self.visit(element, context))
                if result.should_return():
                    return result

                args.append(value)

        try:
            if isinstance(name, PysFunction):
                name._position = node.position
                name._context = context
            elif isinstance(name, PysMethod):
                name.function._position = node.position
                name.function._context = context

            return result.success(name(*args, **kwargs))

        except PysShouldReturn as e:
            result.register(e.result)
            return result

        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    def visit_ReturnNode(self, node, context):
        result = PysRunTimeResult()

        if node.expression:
            value = result.register(self.visit(node.expression, context))
            if result.should_return():
                return result
        else:
            value = None

        return result.success_return(value)

    def visit_ThrowNode(self, node, context):
        result = PysRunTimeResult()

        exception = result.register(self.visit(node.node, context))
        if result.should_return():
            return result

        if not is_exception(exception, BaseException):
            return result.failure(
                PysException(
                    TypeError("exceptions must derive from BaseException"),
                    node.node.position,
                    context
                )
            )

        return result.failure(PysException(exception, node.position, context))

    def visit_ContinueNode(self, node, context):
        return PysRunTimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return PysRunTimeResult().success_break()

    def visit_DeleteNode(self, node, context):
        result = PysRunTimeResult()

        for node_instance in node.objects:

            if isinstance(node_instance, PysAccessNode):
                try:
                    if not context.symbol_table.remove(node_instance.name.value):
                        return result.failure(
                            PysException(
                                NameError(
                                    "'{}' is not defined".format(node_instance.name.value)
                                    if context.symbol_table.get(node_instance.name.value) is undefined else
                                    "'{}' is not defined on local".format(node_instance.name.value)
                                ),
                                node.position,
                                context
                            )
                        )
                except BaseException as e:
                    return result.failure(PysException(e, node.position, context))

            elif isinstance(node_instance, PysSubscriptNode):
                object = result.register(self.visit(node_instance.object, context))
                if result.should_return():
                    return result

                slice = visit_slice_from_SubscriptNode(self, result, node_instance.slice, context)
                if result.should_return():
                    return result

                try:
                    del object[slice]
                except BaseException as e:
                    return result.failure(PysException(e, node_instance.position, context))

            elif isinstance(node_instance, PysAttributeNode):
                object = result.register(self.visit(node_instance.object, context))

                try:
                    delattr(object, node_instance.attribute.name.value)
                except BaseException as e:
                    return result.failure(PysException(e, node_instance.position, context))

        return result.success(undefined)