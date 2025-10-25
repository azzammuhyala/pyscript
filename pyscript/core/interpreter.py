from .bases import Pys
from .constants import TOKENS, KEYWORDS, PYTHON_EXTENSIONS, OPTIMIZE
from .context import PysContext
from .exceptions import PysException
from .handlers import handle_call, handle_exception
from .nodes import PysSequenceNode, PysIdentifierNode, PysAttributeNode, PysSubscriptNode
from .objects import PysFunction
from .pysbuiltins import ce, nce, increment, decrement
from .results import PysRunTimeResult
from .singletons import undefined
from .symtab import PysClassSymbolTable
from .utils import inplace_functions_map, keyword_identifiers_map, is_object_of, get_closest, Iterable

import os

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

        register = result.register
        should_return = result.should_return
        visit = self.visit
        append = elements.append
        ntype = node.type

        if ntype == 'dict':

            for key, value in node.elements:
                key = register(visit(key, context))
                if should_return():
                    return result

                value = register(visit(value, context))
                if should_return():
                    return result

                append((key, value))

        else:

            for element in node.elements:
                append(register(visit(element, context)))
                if should_return():
                    return result

        with handle_exception(result, context, node.position):
            if ntype == 'tuple':
                elements = tuple(elements)
            elif ntype == 'dict':
                elements = dict(elements)
            elif ntype == 'set':
                elements = set(elements)

        if should_return():
            return result

        return result.success(elements)

    def visit_IdentifierNode(self, node, context):
        result = PysRunTimeResult()

        position = node.position
        name = node.token.value
        symbol_table = context.symbol_table

        with handle_exception(result, context, position):
            value = symbol_table.get(name)

            if value is undefined:
                closest_symbol = symbol_table.find_closest(name)

                result.failure(
                    PysException(
                        NameError(
                            "{!r} is not defined{}".format(
                                name,
                                '' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol)
                            )
                        ),
                        context,
                        position
                    )
                )

        if result.should_return():
            return result

        return result.success(value)

    def visit_KeywordNode(self, node, context):
        return PysRunTimeResult().success(keyword_identifiers_map[node.token.value.lower()])

    def visit_AttributeNode(self, node, context):
        result = PysRunTimeResult()

        should_return = result.should_return
        attribute = node.attribute

        object = result.register(self.visit(node.object, context))
        if should_return():
            return result

        with handle_exception(result, context, attribute.position):
            value = getattr(object, attribute.value)

        if should_return():
            return result

        return result.success(value)

    def visit_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return

        object = register(self.visit(node.object, context))
        if should_return():
            return result

        slice = register(self.visit_slice_from_SubscriptNode(node.slice, context))
        if should_return():
            return result

        with handle_exception(result, context, node.position):
            value = object[slice]

        if should_return():
            return result

        return result.success(value)

    def visit_AssignNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return

        value = register(self.visit(node.value, context))
        if should_return():
            return result

        register(self.visit_unpack_AssignNode(node.target, context, value, node.operand.type))
        if should_return():
            return result

        return result.success(value)

    def visit_ChainOperatorNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        position = node.position
        expressions = node.expressions

        left = register(visit(expressions[0], context))
        if should_return():
            return result

        with handle_exception(result, context, position):
            value = True

            for i, operand in enumerate(node.operations):
                omatch = operand.match
                otype = operand.type

                right = register(visit(expressions[i + 1], context))
                if should_return():
                    break

                if omatch(TOKENS['KEYWORD'], KEYWORDS['in']):
                    comparison = left in right
                elif omatch(TOKENS['KEYWORD'], KEYWORDS['is']):
                    comparison = left is right
                elif otype == TOKENS['NOTIN']:
                    comparison = left not in right
                elif otype == TOKENS['ISNOT']:
                    comparison = left is not right
                elif otype == TOKENS['EE']:
                    comparison = left == right
                elif otype == TOKENS['NE']:
                    comparison = left != right
                elif otype == TOKENS['CE']:
                    handle_call(ce, context, position)
                    comparison = ce(left, right)
                elif otype == TOKENS['NCE']:
                    handle_call(nce, context, position)
                    comparison = nce(left, right)
                elif otype == TOKENS['LT']:
                    comparison = left < right
                elif otype == TOKENS['GT']:
                    comparison = left > right
                elif otype == TOKENS['LTE']:
                    comparison = left <= right
                elif otype == TOKENS['GTE']:
                    comparison = left >= right

                if not comparison:
                    value = False
                    break

                left = right

        if should_return():
            return result

        return result.success(value)

    def visit_TernaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit

        condition = register(visit(node.condition, context))
        if should_return():
            return result

        value = register(visit(node.valid if condition else node.invalid, context))
        if should_return():
            return result

        return result.success(value)

    def visit_BinaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        omatch = node.operand.match
        otype = node.operand.type

        left = register(visit(node.left, context))
        if should_return():
            return result

        return_right = True

        if omatch(TOKENS['KEYWORD'], KEYWORDS['and']) or otype == TOKENS['CAND']:
            if not left:
                return result.success(left)

        elif omatch(TOKENS['KEYWORD'], KEYWORDS['or']) or otype == TOKENS['COR']:
            if left:
                return result.success(left)

        elif otype == TOKENS['NULLISH']:
            if left is not None:
                return result.success(left)

        else:
            return_right = False

        right = register(visit(node.right, context))
        if should_return():
            return result

        if return_right:
            return result.success(right)

        with handle_exception(result, context, node.position):

            if otype == TOKENS['PLUS']:
                value = left + right
            elif otype == TOKENS['MINUS']:
                value = left - right
            elif otype == TOKENS['MUL']:
                value = left * right
            elif otype == TOKENS['DIV']:
                value = left / right
            elif otype == TOKENS['FDIV']:
                value = left // right
            elif otype == TOKENS['MOD']:
                value = left % right
            elif otype == TOKENS['AT']:
                value = left @ right
            elif otype == TOKENS['POW']:
                value = left ** right
            elif otype == TOKENS['AND']:
                value = left & right
            elif otype == TOKENS['OR']:
                value = left | right
            elif otype == TOKENS['XOR']:
                value = left ^ right
            elif otype == TOKENS['LSHIFT']:
                value = left << right
            elif otype == TOKENS['RSHIFT']:
                value = left >> right

        if should_return():
            return result

        return result.success(value)

    def visit_UnaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        position = node.position
        otype = node.operand.type

        value = register(visit(node.value, context))
        if should_return():
            return result

        with handle_exception(result, context, position):

            if node.operand.match(TOKENS['KEYWORD'], KEYWORDS['not']):
                new_value = not value
            elif otype == TOKENS['PLUS']:
                new_value = +value
            elif otype == TOKENS['MINUS']:
                new_value = -value
            elif otype == TOKENS['NOT']:
                new_value = ~value

            elif otype in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
                new_value = value

                func = increment if otype == TOKENS['INCREMENT'] else decrement

                handle_call(func, context, position)
                value = func(value)

                if node.operand_position == 'left':
                    new_value = value

                register(self.visit_unpack_AssignNode(node.value, context, value))

        if should_return():
            return result

        return result.success(new_value)

    def visit_ImportNode(self, node, context):
        result = PysRunTimeResult()

        should_return = result.should_return
        get_symbol = context.symbol_table.get
        set_symbol = context.symbol_table.set
        packages = node.packages
        name, as_name = node.name

        with handle_exception(result, context, name.position):
            name_module = name.value
            file, extension = os.path.splitext(name_module)

            if extension in PYTHON_EXTENSIONS:
                name_module = file
                use_python_package = True
            else:
                use_python_package = False

            if not use_python_package:
                require = get_symbol('require')

                if require is undefined:
                    use_python_package = True
                else:
                    handle_call(require, context, name.position)
                    try:
                        module = require(name_module)
                    except ModuleNotFoundError:
                        use_python_package = True

            if use_python_package:
                pyimport = get_symbol('pyimport')

                if pyimport is undefined:
                    result.failure(
                        PysException(
                            NameError("'pyimport' is not defined"),
                            context,
                            node.position
                        )
                    )

                else:
                    handle_call(pyimport, context, name.position)
                    module = pyimport(name_module)

        if should_return():
            return result

        if packages == 'all':

            with handle_exception(result, context, name.position):
                for package in getattr(module, '__all__',
                                       (package for package in dir(module) if not package.startswith('_'))):
                    set_symbol(package, getattr(module, package))

            if should_return():
                return result

        elif packages:

            for package, as_package in packages:

                with handle_exception(result, context, package.position):
                    set_symbol(
                        (package if as_package is None else as_package).value,
                        getattr(module, package.value)
                    )

                if should_return():
                    return result

        elif not (name.type == TOKENS['STRING'] and as_name is None):

            with handle_exception(result, context, node.position):
                set_symbol((name if as_name is None else as_name).value, module)

            if should_return():
                return result

        return result.success(None)

    def visit_IfNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        else_body = node.else_body

        for condition, body in node.cases_body:
            condition_value = register(visit(condition, context))
            if should_return():
                return result

            if condition_value:
                register(visit(body, context))
                if should_return():
                    return result

                return result.success(None)

        if else_body:
            register(visit(else_body, context))
            if should_return():
                return result

        return result.success(None)

    def visit_SwitchNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        default_body = node.default_body

        fall_through = False
        no_match_found = True

        target = register(visit(node.target, context))
        if should_return():
            return result

        for condition, body in node.cases_body:
            case = register(visit(condition, context))
            if should_return():
                return result

            with handle_exception(result, context, condition.position):
                equal = target == case

            if should_return():
                return result

            if fall_through or equal:
                no_match_found = False

                register(visit(body, context))
                if should_return() and not result.should_break:
                    return result

                if result.should_break:
                    result.should_break = False
                    fall_through = False
                else:
                    fall_through = True

        if (fall_through or no_match_found) and default_body:
            register(visit(default_body, context))
            if should_return() and not result.should_break:
                return result

            result.should_break = False

        return result.success(None)

    def visit_TryNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        catch_body = node.catch_body
        error_variable = node.error_variable
        else_body = node.else_body
        finally_body = node.finally_body

        register(visit(node.body, context))

        if catch_body:

            if result.error:

                if error_variable:

                    with handle_exception(result, context, error_variable.position):
                        context.symbol_table.set(error_variable.value, result.error.exception)
                        result.error = None

                    if should_return():
                        return result

                else:
                    result.error = None

                register(visit(catch_body, context))

            elif else_body:
                register(visit(else_body, context))

        if finally_body:
            finally_result = PysRunTimeResult()

            finally_result.register(visit(finally_body, context))
            if finally_result.should_return():
                return finally_result

        if should_return():
            return result

        return result.success(None)

    def visit_ForNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        init = node.init
        init_length = len(init)
        body = node.body
        else_body = node.else_body

        target = init[0]

        if init_length == 2:
            iterator = init[1]
            target_position = target.position
            visit_unpack_AssignNode = self.visit_unpack_AssignNode

            iter_object = register(visit(iterator, context))
            if should_return():
                return result

            with handle_exception(result, context, iterator.position):
                iter_object = iter(iter_object)

            if should_return():
                return result

            def condition():
                with handle_exception(result, context, target_position):
                    register(visit_unpack_AssignNode(target, context, next(iter_object)))

                if should_return():
                    if is_object_of(result.error.exception, StopIteration):
                        result.error = None
                    return False

                return True

            def update():
                pass

        elif init_length == 3:
            conditor = init[1]
            updater = init[2]

            if target:
                register(visit(target, context))
                if should_return():
                    return result

            if conditor:
                def condition():
                    value = register(visit(conditor, context))
                    if should_return():
                        return False
                    return value

            else:
                def condition():
                    return True

            if updater:
                def update():
                    register(visit(updater, context))

            else:
                def update():
                    pass

        while True:
            done = condition()
            if should_return():
                return result

            if not done:
                break

            if body:
                register(visit(body, context))
                if should_return() and not result.should_continue and not result.should_break:
                    return result

                if result.should_continue:
                    result.should_continue = False

                elif result.should_break:
                    break

            update()
            if should_return():
                return result

        if result.should_break:
            result.should_break = False

        elif else_body:
            register(visit(else_body, context))
            if should_return():
                return result

        return result.success(None)

    def visit_WhileNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        ncondition = node.condition
        body = node.body
        else_body = node.else_body

        while True:
            condition = register(visit(ncondition, context))
            if should_return():
                return result

            if not condition:
                break

            if body:
                register(visit(body, context))
                if should_return() and not result.should_continue and not result.should_break:
                    return result

                if result.should_continue:
                    result.should_continue = False

                elif result.should_break:
                    break

        if result.should_break:
            result.should_break = False

        elif else_body:
            register(visit(else_body, context))
            if should_return():
                return result

        return result.success(None)

    def visit_DoWhileNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        ncondition = node.condition
        body = node.body
        else_body = node.else_body

        while True:
            if body:
                register(visit(body, context))
                if should_return() and not result.should_continue and not result.should_break:
                    return result

                if result.should_continue:
                    result.should_continue = False

                elif result.should_break:
                    break

            condition = register(visit(ncondition, context))
            if should_return():
                return result

            if not condition:
                break

        if result.should_break:
            result.should_break = False

        elif else_body:
            register(visit(else_body, context))
            if should_return():
                return result

        return result.success(None)

    def visit_ClassNode(self, node, context):
        result = PysRunTimeResult()

        bases = []

        register = result.register
        should_return = result.should_return
        visit = self.visit
        append = bases.append
        name = node.name.value
        qualname = context.qualname
        symbol_table = context.symbol_table

        for base in node.bases:
            append(register(visit(base, context)))
            if should_return():
                return result

        class_context = PysContext(
            file=context.file,
            name=name,
            qualname=('' if qualname is None else qualname + '.') + name,
            symbol_table=PysClassSymbolTable(symbol_table),
            parent=context,
            parent_entry_position=node.position
        )

        register(visit(node.body, class_context))
        if should_return():
            return result

        with handle_exception(result, context, node.position):
            cls = type(name, tuple(bases), class_context.symbol_table.symbols)
            cls.__qualname__ = class_context.qualname

        if should_return():
            return result

        for decorator in reversed(node.decorators):
            decorator_func = register(visit(decorator, context))
            if should_return():
                return result

            with handle_exception(result, context, decorator.position):
                cls = decorator_func(cls)

            if should_return():
                return result

        with handle_exception(result, context, node.position):
            symbol_table.set(name, cls)

        if should_return():
            return result

        return result.success(None)

    def visit_FunctionNode(self, node, context):
        result = PysRunTimeResult()

        parameters = []

        register = result.register
        should_return = result.should_return
        visit = self.visit
        append = parameters.append
        name = node.name

        for parameter in node.parameters:

            if isinstance(parameter, tuple):
                value = register(visit(parameter[1], context))
                if should_return():
                    return result

                append((parameter[0].value, value))

            else:
                append(parameter.value)

        func = PysFunction(
            name=None if name is None else name.value,
            qualname=context.qualname,
            parameters=parameters,
            body=node.body,
            position=node.position,
            context=context
        )

        for decorator in reversed(node.decorators):
            decorator_func = register(visit(decorator, context))
            if should_return():
                return result

            with handle_exception(result, context, decorator.position):
                func = decorator_func(func)

            if should_return():
                return result

        if name is not None:

            with handle_exception(result, context, node.position):
                context.symbol_table.set(name.value, func)

            if should_return():
                return result

        return result.success(func)

    def visit_CallNode(self, node, context):
        result = PysRunTimeResult()

        args = []
        kwargs = {}

        register = result.register
        should_return = result.should_return
        visit = self.visit
        append = args.append
        setitem = kwargs.__setitem__
        position = node.position

        name = register(visit(node.name, context))
        if should_return():
            return result

        for argument in node.arguments:

            if isinstance(argument, tuple):
                setitem(argument[0].value, register(visit(argument[1], context)))
                if should_return():
                    return result

            else:
                append(register(visit(argument, context)))
                if should_return():
                    return result

        with handle_exception(result, context, position):
            handle_call(name, context, position)
            value = name(*args, **kwargs)

        if should_return():
            return result

        return result.success(value)

    def visit_ReturnNode(self, node, context):
        result = PysRunTimeResult()

        if node.value:
            value = result.register(self.visit(node.value, context))
            if result.should_return():
                return result

            return result.success_return(value)

        return result.success_return(None)

    def visit_GlobalNode(self, node, context):
        context.symbol_table.globals.update(name.value for name in node.names)
        return PysRunTimeResult().success(None)

    def visit_DeleteNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit
        symbol_table = context.symbol_table

        for target in node.targets:

            if isinstance(target, PysIdentifierNode):

                with handle_exception(result, context, target.position):
                    name = target.token.value
                    success = symbol_table.remove(name)

                    if not success:
                        closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                        result.failure(
                            PysException(
                                NameError(
                                    (
                                        "{!r} is not defined".format(name)
                                        if symbol_table.get(name) is undefined else
                                        "{!r} is not defined on local".format(name)
                                    ) +
                                    ('' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol))
                                ),
                                context,
                                target.position
                            )
                        )

                if should_return():
                    return result

            elif isinstance(target, PysSubscriptNode):
                object = register(visit(target.object, context))
                if should_return():
                    return result

                slice = register(self.visit_slice_from_SubscriptNode(target.slice, context))
                if should_return():
                    return result

                with handle_exception(result, context, target.position):
                    del object[slice]

                if should_return():
                    return result

            elif isinstance(target, PysAttributeNode):
                object = register(visit(target.object, context))
                if should_return():
                    return result

                with handle_exception(result, context, target.position):
                    delattr(object, target.attribute.value)

                if should_return():
                    return result

        return result.success(None)

    def visit_ThrowNode(self, node, context):
        result = PysRunTimeResult()

        target = result.register(self.visit(node.target, context))
        if result.should_return():
            return result

        if not is_object_of(target, BaseException):
            return result.failure(
                PysException(
                    TypeError("exceptions must derive from BaseException"),
                    context,
                    node.target.position
                )
            )

        return result.failure(PysException(target, context, node.position))

    def visit_AssertNode(self, node, context):
        result = PysRunTimeResult()

        if not (context.flags & OPTIMIZE):
            register = result.register
            should_return = result.should_return
            visit = self.visit

            condition = register(visit(node.condition, context))
            if should_return():
                return result

            if not condition:

                if node.message:
                    message = register(visit(node.message, context))
                    if should_return():
                        return result

                    return result.failure(PysException(AssertionError(message), context, node.position))

                return result.failure(PysException(AssertionError, context, node.position))

        return result.success(None)

    def visit_EllipsisNode(self, node, context):
        return PysRunTimeResult().success(Ellipsis)

    def visit_ContinueNode(self, node, context):
        return PysRunTimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return PysRunTimeResult().success_break()

    def visit_slice_from_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit

        if isinstance(node, list):
            slices = []

            append = slices.append
            visit_slice_from_SubscriptNode = self.visit_slice_from_SubscriptNode

            for element in node:
                append(register(visit_slice_from_SubscriptNode(element, context)))
                if should_return():
                    return result

            return result.success(tuple(slices))

        elif isinstance(node, tuple):
            start, stop, step = node

            if start is not None:
                start = register(visit(start, context))
                if should_return():
                    return result

            if stop is not None:
                stop = register(visit(stop, context))
                if should_return():
                    return result

            if step is not None:
                step = register(visit(step, context))
                if should_return():
                    return result

            return result.success(slice(start, stop, step))

        else:
            value = register(visit(node, context))
            if should_return():
                return result

            return result.success(value)

    def visit_unpack_AssignNode(self, node, context, value, operand=TOKENS['EQ']):
        result = PysRunTimeResult()

        register = result.register
        should_return = result.should_return
        visit = self.visit

        if isinstance(node, PysSequenceNode):

            if not isinstance(value, Iterable):
                return result.failure(
                    PysException(
                        TypeError("cannot unpack non-iterable"),
                        context,
                        node.position
                    )
                )

            count = 0

            with handle_exception(result, context, node.position):
                elements = node.elements
                elements_length = len(elements)

                for i, element in enumerate(value):

                    if i < elements_length:
                        register(self.visit_unpack_AssignNode(elements[i], context, element, operand))
                        if should_return():
                            return result

                        count += 1

                    else:
                        result.failure(
                            PysException(
                                ValueError("to many values to unpack (expected {})".format(elements_length)),
                                context,
                                node.position
                            )
                        )

                        break

            if should_return():
                return result

            if count < elements_length:
                return result.failure(
                    PysException(
                        ValueError(
                            "not enough values to unpack (expected {}, got {})".format(elements_length, count)
                        ),
                        context,
                        node.position
                    )
                )

        elif isinstance(node, PysSubscriptNode):
            object = register(visit(node.object, context))
            if should_return():
                return result

            slice = register(self.visit_slice_from_SubscriptNode(node.slice, context))
            if should_return():
                return result

            with handle_exception(result, context, node.position):
                if operand == TOKENS['EQ']:
                    object[slice] = value
                else:
                    object[slice] = inplace_functions_map[operand](object[slice], value)

            if should_return():
                return result

        elif isinstance(node, PysAttributeNode):
            object = register(visit(node.object, context))
            if should_return():
                return result

            attribute = node.attribute.value

            with handle_exception(result, context, node.position):
                if operand == TOKENS['EQ']:
                    setattr(object, attribute, value)
                else:
                    setattr(
                        object,
                        attribute,
                        inplace_functions_map[operand](getattr(object, attribute), value)
                    )

            if should_return():
                return result

        elif isinstance(node, PysIdentifierNode):

            with handle_exception(result, context, node.position):
                symbol_table = context.symbol_table
                name = node.token.value

                success = symbol_table.set(name, value, operand)

                if not success:
                    closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                    result.failure(
                        PysException(
                            NameError(
                                (
                                    "{!r} is not defined".format(name)
                                    if symbol_table.get(name) is undefined else
                                    "{!r} is not defined on local".format(name)
                                ) + ('' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol))
                            ),
                            context,
                            node.position
                        )
                    )

            if should_return():
                return result

        return result.success(None)

interpreter = PysInterpreter()