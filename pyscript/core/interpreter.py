from .constants import (
    TOKENS, KEYWORDS,
    DEBUG,
    NSEQ_STATEMENTS, NSEQ_GLOBAL, NSEQ_DEL, NSEQ_DICT, NSEQ_SET, NSEQ_LIST, NSEQ_TUPLE,
    NUNR_LEFT,
    NIMP_ALL
)
from .cache import undefined
from .context import PysClassContext
from .exceptions import PysException
from .handlers import handle_exception, handle_call
from .nodes import PysNode, PysIdentifierNode, PysSequenceNode, PysAttributeNode, PysSubscriptNode
from .objects import PysFunction
from .pysbuiltins import ce, nce, increment, decrement
from .results import PysRunTimeResult
from .symtab import PysClassSymbolTable
from .utils.constants import BINARY_FUNCTIONS_MAP, UNARY_FUNCTIONS_MAP, KEYWORDS_TO_VALUES_MAP, PYTHON_EXTENSIONS
from .utils.general import setimuattr, get_closest, get_error_args, is_object_of

from collections.abc import Iterable
from os.path import splitext as split_file_extension

def visit(node, context):
    return visitors[node.__class__](node, context)

def visit_NumberNode(node, context):
    return PysRunTimeResult().success(node.token.value)

def visit_StringNode(node, context):
    return PysRunTimeResult().success(node.token.value)

def visit_SequenceNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntype = node.type

    if ntype == NSEQ_STATEMENTS:
        elements = node.elements

        if len(elements) == 1:
            value = register(visit(elements[0], context))
            if should_return():
                return result

            return result.success(value)

        for element in elements:
            register(visit(element, context))
            if should_return():
                return result

        return result.success(None)

    elif ntype == NSEQ_GLOBAL:
        context.symbol_table.globals.update(name.value for name in node.elements)
        return result.success(None)

    elif ntype == NSEQ_DEL:
        symbol_table = context.symbol_table

        for element in node.elements:

            if isinstance(element, PysIdentifierNode):
                name = element.token.value

                with handle_exception(result, context, element.position):

                    if not symbol_table.remove(name):
                        closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                        return result.failure(
                            PysException(
                                NameError(
                                    (
                                        f"{name!r} is not defined"
                                        if symbol_table.get(name) is undefined else
                                        f"{name!r} is not defined on local"
                                    )
                                    +
                                    (
                                        ''
                                        if closest_symbol is None else
                                        f". Did you mean {closest_symbol!r}?"
                                    )
                                ),
                                context,
                                element.position
                            )
                        )

                if should_return():
                    return result

            elif isinstance(element, PysAttributeNode):
                target = register(visit(element.target, context))
                if should_return():
                    return result

                with handle_exception(result, context, element.position):
                    delattr(target, element.attribute.value)

                if should_return():
                    return result

            elif isinstance(element, PysSubscriptNode):
                target = register(visit(element.target, context))
                if should_return():
                    return result

                slice = register(visit_slice_SubscriptNode(element.slice, context))
                if should_return():
                    return result

                with handle_exception(result, context, element.position):
                    del target[slice]

                if should_return():
                    return result

        return result.success(None)

    elif ntype == NSEQ_DICT:
        elements = {}
        setitem = elements.__setitem__

        for nkey, nvalue in node.elements:
            key = register(visit(nkey, context))
            if should_return():
                return result

            value = register(visit(nvalue, context))
            if should_return():
                return result

            with handle_exception(result, context, nkey.position):
                setitem(key, value)

            if should_return():
                return result

        return result.success(elements)

    elif ntype == NSEQ_SET:
        elements = set()
        add = elements.add

        for element in node.elements:

            with handle_exception(result, context, element.position):
                add(register(visit(element, context)))

            if should_return():
                return result

        return result.success(elements)

    elements = []
    append = elements.append

    for element in node.elements:
        append(register(visit(element, context)))
        if should_return():
            return result

    if ntype == NSEQ_LIST:
        return result.success(elements)
    elif ntype == NSEQ_TUPLE:
        return result.success(tuple(elements))

def visit_IdentifierNode(node, context):
    result = PysRunTimeResult()

    position = node.position
    name = node.token.value
    symbol_table = context.symbol_table

    with handle_exception(result, context, position):
        value = symbol_table.get(name)

        if value is undefined:
            closest_symbol = symbol_table.find_closest(name)

            return result.failure(
                PysException(
                    NameError(
                        f"{name!r} is not defined" +
                        (
                            ''
                            if closest_symbol is None else
                            f". Did you mean {closest_symbol!r}?"
                        )
                    ),
                    context,
                    position
                )
            )

    if result.should_return():
        return result

    return result.success(value)

def visit_KeywordNode(node, context):
    value = node.token.value

    return PysRunTimeResult().success(
        bool(context.flags & DEBUG)
        if value == KEYWORDS['__debug__'] else
        KEYWORDS_TO_VALUES_MAP[value]
    )

def visit_AttributeNode(node, context):
    result = PysRunTimeResult()

    should_return = result.should_return
    attribute = node.attribute

    target = result.register(visit(node.target, context))
    if should_return():
        return result

    with handle_exception(result, context, attribute.position):
        return result.success(getattr(target, attribute.value))

    if should_return():
        return result

def visit_SubscriptNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return

    target = register(visit(node.target, context))
    if should_return():
        return result

    slice = register(visit_slice_SubscriptNode(node.slice, context))
    if should_return():
        return result

    with handle_exception(result, context, node.position):
        return result.success(target[slice])

    if should_return():
        return result

def visit_ChainOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    position = node.position
    expressions = node.expressions

    left = register(visit(expressions[0], context))
    if should_return():
        return result

    with handle_exception(result, context, position):

        for i, operand in enumerate(node.operations):
            omatch = operand.match
            otype = operand.type

            right = register(visit(expressions[i + 1], context))
            if should_return():
                return result

            if omatch(TOKENS['KEYWORD'], KEYWORDS['in']):
                value = left in right
            elif omatch(TOKENS['KEYWORD'], KEYWORDS['is']):
                value = left is right
            elif otype == TOKENS['CE']:
                handle_call(ce, context, position)
                value = ce(left, right)
            elif otype == TOKENS['NCE']:
                handle_call(nce, context, position)
                value = nce(left, right)
            else:
                value = BINARY_FUNCTIONS_MAP[otype](left, right)

            if not value:
                break

            left = right

    if should_return():
        return result

    return result.success(value)

def visit_TernaryOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ncondition = node.condition

    condition = register(visit(ncondition, context))
    if should_return():
        return result

    with handle_exception(result, context, ncondition.position):
        value = register(visit(node.valid if condition else node.invalid, context))

    if should_return():
        return result

    return result.success(value)

def visit_BinaryOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    omatch = node.operand.match
    otype = node.operand.type

    left = register(visit(node.left, context))
    if should_return():
        return result

    return_right = True

    with handle_exception(result, context, node.position):

        if omatch(TOKENS['KEYWORD'], KEYWORDS['and']) or otype == TOKENS['CAND']:
            if not left: return result.success(left)
        elif omatch(TOKENS['KEYWORD'], KEYWORDS['or']) or otype == TOKENS['COR']:
            if left: return result.success(left)
        elif otype == TOKENS['NULLISH']:
            if left is not None: return result.success(left)
        else:
            return_right = False

        right = register(visit(node.right, context))
        if should_return():
            return result

        return result.success(
            right
            if return_right else
            BINARY_FUNCTIONS_MAP[otype](left, right)
        )

    if should_return():
        return result

def visit_UnaryOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    position = node.position
    otype = node.operand.type

    value = register(visit(node.value, context))
    if should_return():
        return result

    with handle_exception(result, context, position):

        if node.operand.match(TOKENS['KEYWORD'], KEYWORDS['not']) or otype == TOKENS['CNOT']:
            return result.success(not value)

        elif otype in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            new_value = value

            func = increment if otype == TOKENS['INCREMENT'] else decrement
            handle_call(func, context, position)
            value = func(value)

            if node.operand_position == NUNR_LEFT:
                new_value = value

            register(visit_declaration_AssignNode(node.value, context, value))
            if should_return():
                return result

            return result.success(new_value)

        return result.success(UNARY_FUNCTIONS_MAP[otype](value))

    if should_return():
        return result

def visit_AssignNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return

    value = register(visit(node.value, context))
    if should_return():
        return result

    register(visit_declaration_AssignNode(node.target, context, value, node.operand.type))
    if should_return():
        return result

    return result.success(value)

def visit_ImportNode(node, context):
    result = PysRunTimeResult()

    should_return = result.should_return
    get_symbol = context.symbol_table.get
    set_symbol = context.symbol_table.set
    packages = node.packages
    name, as_name = node.name
    name_position = name.position

    with handle_exception(result, context, name_position):
        name_module = name.value
        file, extension = split_file_extension(name_module)

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
                handle_call(require, context, name_position)
                try:
                    module = require(name_module)
                except ModuleNotFoundError:
                    use_python_package = True

        if use_python_package:
            pyimport = get_symbol('pyimport')

            if pyimport is undefined:
                pyimport = get_symbol('__import__')

                if pyimport is undefined:
                    return result.failure(
                        PysException(
                            NameError("'require', 'pyimport', and '__import__' is not defined"),
                            context,
                            node.position
                        )
                    )

            handle_call(pyimport, context, name_position)
            module = pyimport(name_module)

    if should_return():
        return result

    if packages == NIMP_ALL:

        with handle_exception(result, context, name_position):
            for package in getattr(
                module, '__all__',
                (package for package in dir(module) if not package.startswith('_'))
            ):
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

def visit_IfNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    else_body = node.else_body

    for condition, body in node.cases_body:
        condition_value = register(visit(condition, context))
        if should_return():
            return result

        with handle_exception(result, context, condition.position):
            condition_value = True if condition_value else False

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

def visit_SwitchNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    default_body = node.default_body

    fall_through = False
    no_match_found = True

    target = register(visit(node.target, context))
    if should_return():
        return result

    for condition, body in node.case_cases:
        case = register(visit(condition, context))
        if should_return():
            return result

        with handle_exception(result, context, condition.position):
            equal = True if target == case else False

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

def visit_TryNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    else_body = node.else_body
    finally_body = node.finally_body

    register(visit(node.body, context))

    error = result.error

    if error:
        exception = error.exception
        result.error = None

        for (error_name, parameter), body in node.catch_cases:

            if error_name:
                error_cls = register(visit_IdentifierNode(error_name, context))
                if result.error:
                    setimuattr(result.error, 'other', error)
                    break

                if not (isinstance(error_cls, type) and issubclass(error_cls, BaseException)):
                    return result.failure(
                        PysException(
                            TypeError("catching classes that do not inherit from BaseException is not allowed"),
                            context,
                            error_name.position,
                            error
                        )
                    )

            if error_name is None or is_object_of(exception, error_cls):

                if parameter:

                    with handle_exception(result, context, parameter.position):
                        context.symbol_table.set(parameter.value, error.exception)

                    if should_return():
                        return result

                register(visit(body, context))
                if result.error:
                    setimuattr(result.error, 'other', error)

                break

        else:
            result.error = error

    elif else_body:
        register(visit(else_body, context))

    if finally_body:
        finally_result = PysRunTimeResult()

        finally_result.register(visit(finally_body, context))
        if finally_result.should_return():
            if finally_result.error:
                setimuattr(finally_result.error, 'other', result.error)
            return finally_result

    if should_return():
        return result

    return result.success(None)

def visit_WithNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ncontext = node.context
    ncontext_position = ncontext.position
    alias = node.alias

    context_value = register(visit(ncontext, context))
    if should_return():
        return result

    with handle_exception(result, context, ncontext_position):
        enter = context_value.__enter__
        handle_call(enter, context, ncontext_position)
        enter_value = enter()

    if should_return():
        return result

    if alias:

        with handle_exception(result, context, alias.position):
            context.symbol_table.set(alias.value, enter_value)

        if should_return():
            return result

    register(visit(node.body, context))

    error = result.error

    with handle_exception(result, context, ncontext_position):
        exit = context_value.__exit__
        handle_call(exit, context, ncontext_position)
        if exit(*get_error_args(error)):
            result.error = None

    if should_return():
        if result.error and result.error is not error:
            setimuattr(result.error, 'other', error)
        return result

    return result.success(None)

def visit_ForNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    header = node.header
    header_length = len(header)
    body = node.body
    else_body = node.else_body

    if header_length == 2:
        declaration, iteration = header
        iteration_position = iteration.position

        iteration_object = register(visit(iteration, context))
        if should_return():
            return result

        with handle_exception(result, context, iteration_position):
            handle_call(getattr(iteration_object, '__iter__', None), context, iteration_position)
            iteration_object = iter(iteration_object)

        if should_return():
            return result

        def condition():
            with handle_exception(result, context, iteration_position):
                handle_call(iteration_object.__next__, context, iteration_position)
                register(visit_declaration_AssignNode(declaration, context, next(iteration_object)))

            if should_return():
                if is_object_of(result.error.exception, StopIteration):
                    result.error = None
                return False

            return True

        def update():
            pass

    elif header_length == 3:
        declaration, ncondition, nupdate = header

        if declaration:
            register(visit(declaration, context))
            if should_return():
                return result

        if ncondition:
            ncondition_position = ncondition.position

            def condition():
                value = register(visit(ncondition, context))
                if should_return():
                    return False

                with handle_exception(result, context, ncondition_position):
                    return True if value else False

        else:
            def condition():
                return True

        if nupdate:
            def update():
                register(visit(nupdate, context))

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

def visit_WhileNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ncondition = node.condition
    ncondition_position = ncondition.position
    body = node.body
    else_body = node.else_body

    while True:
        condition = register(visit(ncondition, context))
        if should_return():
            return result

        with handle_exception(result, context, ncondition_position):
            if not condition:
                break

        if should_return():
            return result

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

def visit_DoWhileNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ncondition = node.condition
    ncondition_position = ncondition.position
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

        with handle_exception(result, context, ncondition_position):
            if not condition:
                break

        if should_return():
            return result

    if result.should_break:
        result.should_break = False

    elif else_body:
        register(visit(else_body, context))
        if should_return():
            return result

    return result.success(None)

def visit_ClassNode(node, context):
    result = PysRunTimeResult()

    bases = []

    register = result.register
    should_return = result.should_return
    append = bases.append
    name = node.name.value
    symbol_table = context.symbol_table

    for base in node.bases:
        append(register(visit(base, context)))
        if should_return():
            return result

    class_context = PysClassContext(
        name=name,
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

def visit_FunctionNode(node, context):
    result = PysRunTimeResult()

    parameters = []

    register = result.register
    should_return = result.should_return
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

def visit_CallNode(node, context):
    result = PysRunTimeResult()

    args = []
    kwargs = {}

    register = result.register
    should_return = result.should_return
    append = args.append
    setitem = kwargs.__setitem__
    position = node.position

    target = register(visit(node.target, context))
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
        handle_call(target, context, position)
        value = target(*args, **kwargs)

    if should_return():
        return result

    return result.success(value)

def visit_ReturnNode(node, context):
    result = PysRunTimeResult()

    if node.value:
        value = result.register(visit(node.value, context))
        if result.should_return():
            return result

        return result.success_return(value)

    return result.success_return(None)

def visit_ThrowNode(node, context):
    result = PysRunTimeResult()

    target = result.register(visit(node.target, context))
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

def visit_AssertNode(node, context):
    result = PysRunTimeResult()

    if not (context.flags & DEBUG):
        register = result.register
        should_return = result.should_return
        ncondition = node.condition

        condition = register(visit(ncondition, context))
        if should_return():
            return result

        with handle_exception(result, context, ncondition.position):

            if not condition:

                if node.message:
                    message = register(visit(node.message, context))
                    if should_return():
                        return result

                    return result.failure(PysException(AssertionError(message), context, node.position))

                return result.failure(PysException(AssertionError, context, node.position))

        if should_return():
            return result

    return result.success(None)

def visit_EllipsisNode(node, context):
    return PysRunTimeResult().success(Ellipsis)

def visit_ContinueNode(node, context):
    return PysRunTimeResult().success_continue()

def visit_BreakNode(node, context):
    return PysRunTimeResult().success_break()

def visit_slice_SubscriptNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return

    if isinstance(node, tuple):
        slices = []

        append = slices.append

        for element in node:
            append(register(visit_slice_SubscriptNode(element, context)))
            if should_return():
                return result

        return result.success(tuple(slices))

    elif isinstance(node, slice):
        start = node.start
        stop = node.stop
        step = node.step

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

def visit_declaration_AssignNode(node, context, value, operand=TOKENS['EQ']):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return

    if isinstance(node, PysIdentifierNode):
        symbol_table = context.symbol_table
        name = node.token.value

        with handle_exception(result, context, node.position):

            if not symbol_table.set(name, value, operand):
                closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                result.failure(
                    PysException(
                        NameError(
                            (
                                f"{name!r} is not defined"
                                if symbol_table.get(name) is undefined else
                                f"{name!r} is not defined on local"
                            )
                            +
                            (
                                ''
                                if closest_symbol is None else
                                f". Did you mean {closest_symbol!r}?"
                            )
                        ),
                        context,
                        node.position
                    )
                )

        if should_return():
            return result

    elif isinstance(node, PysAttributeNode):
        target = register(visit(node.target, context))
        if should_return():
            return result

        attribute = node.attribute.value

        with handle_exception(result, context, node.position):
            setattr(
                target,
                attribute,
                value
                if operand == TOKENS['EQ'] else
                BINARY_FUNCTIONS_MAP[operand](getattr(target, attribute), value)
            )

        if should_return():
            return result

    elif isinstance(node, PysSubscriptNode):
        target = register(visit(node.target, context))
        if should_return():
            return result

        slice = register(visit_slice_SubscriptNode(node.slice, context))
        if should_return():
            return result

        with handle_exception(result, context, node.position):
            target[slice] = (
                value
                if operand == TOKENS['EQ'] else
                BINARY_FUNCTIONS_MAP[operand](target[slice], value)
            )

        if should_return():
            return result

    elif isinstance(node, PysSequenceNode):
        position = node.position

        if not isinstance(value, Iterable):
            return result.failure(
                PysException(
                    TypeError(f"cannot unpack non-iterable {type(value).__name__} object"),
                    context,
                    position
                )
            )

        elements = node.elements
        count = 0

        with handle_exception(result, context, position):

            for element, element_value in zip(elements, value):
                register(visit_declaration_AssignNode(element, context, element_value, operand))
                if should_return():
                    return result

                count += 1

        if should_return():
            return result

        length = len(elements)

        if count < length:
            return result.failure(
                PysException(
                    ValueError(f"not enough values to unpack (expected {length}, got {count})"),
                    context,
                    node.position
                )
            )

        elif count > length:
            return result.failure(
                PysException(
                    ValueError(f"to many values to unpack (expected {length})"),
                    context,
                    node.position
                )
            )

    return result.success(None)

visitors = {
    class_node: globals()[f'visit_{class_node.__name__[3:]}']
    for class_node in PysNode.__subclasses__()
}