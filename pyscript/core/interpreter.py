from .bases import Pys
from .exceptions import PysException
from .values import PysShouldReturn, PysValue, PysFunction, PysMethod
from .constants import TOKENS
from .utils import SYNTAX, is_exception, Iterable
from .pysbuiltins import undefined, closeeq, increment, decrement
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

def visit_slices_from_SliceNode(self, result, slices, context):
    if isinstance(slices, tuple):
        start, stop, step = slices

        if start is not None:
            start = result.register(self.visit(start, context))
            if result.should_return():
                return result
            start = start.value

        if stop is not None:
            stop = result.register(self.visit(stop, context))
            if result.should_return():
                return result
            stop = stop.value

        if step is not None:
            step = result.register(self.visit(step, context))
            if result.should_return():
                return result
            step = step.value

        slices = slice(start, stop, step)

    elif isinstance(slices, list):
        slices = []

        for element in slices:
            visit_slices_from_SliceNode(self, result, element, context)
            if result.should_return():
                return result

        slices = tuple(slices)

    else:
        value = result.register(self.visit(slices, context))
        if result.should_return():
            return result

        slices = value.value

    return slices

def unpack_assign(self, result, node, value, context, operand):

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

        slices = visit_slices_from_SliceNode(self, result, node.slice, context)
        if result.should_return():
            return result

        try:
            object.value[slices] = value
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    elif isinstance(node, PysAttributeNode):
        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        try:
            setattr(object.value, node.attribute.name.value, value)
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    elif isinstance(node, PysVariableAccessNode):
        name = node.name.value
        variable = context.symbol_table.get(name)

        if operand == TOKENS['EQ']:
            if variable is undefined:
                context.symbol_table.set(name, value)
            else:
                variable.value = value

        else:

            if variable is undefined:
                return result.failure(
                    PysException(
                        NameError("'{}' is not defined".format(element)),
                        node.position,
                        context
                    )
                )

            if operand == TOKENS['IPLUS']:
                variable.value += value
            elif operand == TOKENS['IMINUS']:
                variable.value -= value
            elif operand == TOKENS['IMUL']:
                variable.value *= value
            elif operand == TOKENS['IDIV']:
                variable.value /= value
            elif operand == TOKENS['IFDIV']:
                variable.value //= value
            elif operand == TOKENS['IPOW']:
                variable.value **= value
            elif operand == TOKENS['IMOD']:
                variable.value %= value
            elif operand == TOKENS['IAND']:
                variable.value &= value
            elif operand == TOKENS['IXOR']:
                variable.value ^= value
            elif operand == TOKENS['ILSHIFT']:
                variable.value <<= value
            elif operand == TOKENS['IRSHIFT']:
                variable.value >>= value

class PysInterpreter(Pys):

    def visit(self, node, context):
        return getattr(self, 'visit_' + type(node).__name__[3:])(node, context)

    def visit_NumberNode(self, node, context):
        return PysRunTimeResult().success(PysValue(node.token.value))

    def visit_StringNode(self, node, context):
        return PysRunTimeResult().success(PysValue(node.token.value))

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

                elements.append((key.value, value.value))

            else:
                value = result.register(self.visit(element, context))
                if result.should_return():
                    return result

                elements.append(value.value)

        try:
            if node.type == 'tuple':
                elements = tuple(elements)
            elif node.type == 'dict':
                elements = dict(elements)
            elif node.type == 'set':
                elements = set(elements)
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

        return result.success(PysValue(elements))

    def visit_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        slice = visit_slices_from_SliceNode(self, result, node.slice, context)
        if result.should_return():
            return result

        try:
            return result.success(PysValue(object.value[slice]))
        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

    def visit_VariableAccessNode(self, node, context):
        result = PysRunTimeResult()
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
            attribute = getattr(object.value, node.attribute.name.value)
        except BaseException as e:
            return result.failure(PysException(e, node.attribute.position, context))

        return result.success(PysValue(attribute))

    def visit_VariableAssignNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        unpack_assign(self, result, node.variable, value.value, context, node.operand.type)
        if result.should_return():
            return result

        return result.success(PysValue(undefined))

    def visit_BinaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        left = result.register(self.visit(node.left, context))
        if result.should_return():
            return result

        if node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['and']):
            if left.value:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                result_value = right.value
            else:
                result_value = left.value

        elif node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['or']):
            if not left.value:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                result_value = right.value
            else:
                result_value = left.value

        else:
            right = result.register(self.visit(node.right, context))
            if result.should_return():
                return result

        try:

            if node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['in']):
                result_value = left.value in right.value
            elif node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['is']):
                result_value = left.value is right.value
            elif node.operand.type == TOKENS['EE']:
                result_value = left.value == right.value
            elif node.operand.type == TOKENS['CE']:
                result_value = closeeq(left.value, right.value)
            elif node.operand.type == TOKENS['NE']:
                result_value = left.value != right.value
            elif node.operand.type == TOKENS['LT']:
                result_value = left.value < right.value
            elif node.operand.type == TOKENS['GT']:
                result_value = left.value > right.value
            elif node.operand.type == TOKENS['LTE']:
                result_value = left.value <= right.value
            elif node.operand.type == TOKENS['GTE']:
                result_value = left.value >= right.value
            elif node.operand.type == TOKENS['AND']:
                result_value = left.value & right.value
            elif node.operand.type == TOKENS['OR']:
                result_value = left.value | right.value
            elif node.operand.type == TOKENS['XOR']:
                result_value = left.value ^ right.value
            elif node.operand.type == TOKENS['LSHIFT']:
                result_value = left.value << right.value
            elif node.operand.type == TOKENS['RSHIFT']:
                result_value = left.value >> right.value
            elif node.operand.type == TOKENS['PLUS']:
                result_value = left.value + right.value
            elif node.operand.type == TOKENS['MINUS']:
                result_value = left.value - right.value
            elif node.operand.type == TOKENS['MUL']:
                result_value = left.value * right.value
            elif node.operand.type == TOKENS['DIV']:
                result_value = left.value / right.value
            elif node.operand.type == TOKENS['FDIV']:
                result_value = left.value // right.value
            elif node.operand.type == TOKENS['MOD']:
                result_value = left.value % right.value
            elif node.operand.type == TOKENS['POW']:
                result_value = left.value ** right.value

        except BaseException as e:
            return result.failure(PysException(e, node.position, context))

        return result.success(PysValue(result_value))

    def visit_UnaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        try:

            if node.operand.match(TOKENS['KEYWORD'], SYNTAX['keywords']['not']):
                result_value = not value.value
            elif node.operand.type == TOKENS['PLUS']:
                result_value = +value.value
            elif node.operand.type == TOKENS['MINUS']:
                result_value = -value.value
            elif node.operand.type == TOKENS['NOT']:
                result_value = ~value.value
            elif node.operand.type == TOKENS['INCREMENT']:
                result_value = value.value
                value.value = increment(value.value)
                if node.operand_position == 'left':
                    result_value = value.value
            elif node.operand.type == TOKENS['DECREMENT']:
                result_value = value.value
                value.value = decrement(value.value)
                if node.operand_position == 'left':
                    result_value = value.value

        except Exception as e:
            return result.failure(PysException(e, node.position, context))

        return result.success(PysValue(result_value))

    def visit_TernaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        condition = result.register(self.visit(node.condition, context))
        if result.should_return():
            return result

        if condition.value:
            result_value = result.register(self.visit(node.valid, context))
            if result.should_return():
                return result
        else:
            result_value = result.register(self.visit(node.invalid, context))
            if result.should_return():
                return result

        return result.success(PysValue(result_value.value))

    def visit_IfNode(self, node, context):
        result = PysRunTimeResult()

        for condition, body in node.cases:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if condition_value.value:
                result.register(self.visit(body, context))
                if result.should_return():
                    return result

                return result.success(PysValue(undefined))

        if node.else_case:
            result.register(self.visit(node.else_case, context))
            if result.should_return():
                return result

        return result.success(PysValue(undefined))

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

            if fall_through or value.value == condition_value.value:
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

        return result.success(PysValue(undefined))

    def visit_ForNode(self, node, context):
        result = PysRunTimeResult()

        if len(node.iterable) == 2:
            iterable = result.register(self.visit(node.iterable[1], context))
            if result.should_return():
                return result

            iterable = iter(iterable.value)

            def condition():
                try:
                    unpack_assign(self, result, node.iterable[0], next(iterable), context, TOKENS['EQ'])
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

                    return value.value

                return True

            def update():
                if node.iterable[2]:
                    result.register(self.visit(node.iterable[2], context))

        while condition():
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

        if result.should_return():
            return result

        return result.success(PysValue(undefined))

    def visit_WhileNode(self, node, context):
        result = PysRunTimeResult()

        while True:
            condition = result.register(self.visit(node.condition, context))
            if result.should_return():
                return result

            if not condition.value:
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

        return result.success(PysValue(undefined))

    def visit_FunctionNode(self, node, context):
        result = PysRunTimeResult()

        parameter = []

        for arg in node.parameter:

            if isinstance(arg, PysVariableAccessNode):
                parameter.append(arg.name.value)

            elif isinstance(arg, tuple):
                value = result.register(self.visit(arg[1], context))
                if result.should_return():
                    return result

                parameter.append((arg[0].name.value, value.value))

        func = PysFunction(
            node.position_parameter,
            context,
            None if node.name is None else node.name.name.value,
            parameter,
            node.body
        )

        if func.name is not None:
            context.symbol_table.set(func.name, func)

        return result.success(PysValue(func))

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

                kwargs[element[0].name.value] = value.value

            else:
                value = result.register(self.visit(element, context))
                if result.should_return():
                    return result

                args.append(value.value)

        try:
            if isinstance(name.value, PysFunction):
                name.value.position = node.position
                name.value.context = context
            elif isinstance(name.value, PysMethod):
                name.value.function.position = node.position
                name.value.function.context = context

            func_return = name.value(*args, **kwargs)

            return result.success(PysValue(func_return))

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
            value = PysValue(None)

        return result.success_return(value)

    def visit_ThrowNode(self, node, context):
        result = PysRunTimeResult()

        exception = result.register(self.visit(node.node, context))
        if result.should_return():
            return result

        if not is_exception(exception.value, BaseException):
            return result.failure(
                PysException(
                    TypeError("exceptions must derive from BaseException"),
                    node.node.position,
                    context
                )
            )

        return result.failure(PysException(exception.value, node.position, context))

    def visit_ContinueNode(self, node, context):
        return PysRunTimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return PysRunTimeResult().success_break()

    def visit_DeleteNode(self, node, context):
        result = PysRunTimeResult()

        for node_instance in node.objects:

            if isinstance(node_instance, PysVariableAccessNode):
                success = context.symbol_table.remove(node_instance.name.value)
                if not success:
                    return result.failure(
                        PysException(
                            NameError("'{}' is not defined".format(node_instance.name.value)),
                            node.position,
                            context
                        )
                    )

            elif isinstance(node_instance, PysSubscriptNode):
                object = result.register(self.visit(node_instance.object, context))
                if result.should_return():
                    return result

                slices = visit_slices_from_SliceNode(self, result, node_instance.slice, context)
                if result.should_return():
                    return result

                try:
                    del object.value[slices]
                except BaseException as e:
                    return result.failure(PysException(e, node_instance.position, context))

            elif isinstance(node_instance, PysAttributeNode):
                object = result.register(self.visit(node_instance.object, context))

                try:
                    delattr(object.value, node_instance.attribute.name.value)
                except BaseException as e:
                    return result.failure(PysException(e, node_instance.position, context))

        return result.success(PysValue(undefined))

    def visit_TryNode(self, node, context):
        result = PysRunTimeResult()

        result.register(self.visit(node.body, context))

        if result.should_return():
            if node.variable:
                context.symbol_table.set(node.variable.name.value, result.error.exception)

            result.register(self.visit(node.catch, context))
            if result.should_return():
                return result

        return result.success(PysValue(undefined))