from .constants import TOKENS, KEYWORDS, DEBUG
from .cache import undefined
from .checks import is_assign, is_python_extensions, is_equals, is_incremental
from .context import PysClassContext
from .exceptions import PysException
from .handlers import handle_exception, handle_call
from .mapping import BINARY_FUNCTIONS_MAP, UNARY_FUNCTIONS_MAP, KEYWORDS_TO_VALUES_MAP
from .nodes import PysNode, PysIdentifierNode, PysAttributeNode, PysSubscriptNode
from .objects import PysFunction
from .pysbuiltins import ce, nce, increment, decrement
from .results import PysRunTimeResult
from .symtab import PysClassSymbolTable, find_closest
from .utils.generic import setimuattr, get_closest, get_error_args, is_object_of

from collections.abc import Iterable
from os.path import splitext as split_file_extension

KW__DEBUG__ = KEYWORDS['__debug__']
KW_AND = KEYWORDS['and']
KW_IN = KEYWORDS['in']
KW_IS = KEYWORDS['is']
KW_NOT = KEYWORDS['not']
KW_OR = KEYWORDS['or']

T_KEYWORD = TOKENS['KEYWORD']
T_STRING = TOKENS['STRING']
T_INCREMENT = TOKENS['DOUBLE-PLUS']
T_AND = TOKENS['DOUBLE-AMPERSAND']
T_OR = TOKENS['DOUBLE-PIPE']
T_NOT = TOKENS['EXCLAMATION']
T_CE = TOKENS['EQUAL-TILDE']
T_NCE = TOKENS['EXCLAMATION-TILDE']
T_NULLISH = TOKENS['DOUBLE-QUESTION']

def visit(node, context):
    return visitors[node.__class__](node, context)

def visit_NumberNode(node, context):
    return PysRunTimeResult().success(node.token.value)

def visit_StringNode(node, context):
    return PysRunTimeResult().success(node.token.value)

def visit_DictionaryNode(node, context):
    result = PysRunTimeResult()

    elements = {}

    register = result.register
    should_return = result.should_return
    setitem = elements.__setitem__

    for nkey, nvalue in node.pairs:
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

def visit_SetNode(node, context):
    result = PysRunTimeResult()

    elements = set()

    register = result.register
    should_return = result.should_return
    add = elements.add

    for nelement in node.elements:

        with handle_exception(result, context, nelement.position):
            add(register(visit(nelement, context)))

        if should_return():
            return result

    return result.success(elements)

def visit_ListNode(node, context):
    result = PysRunTimeResult()

    elements = []

    register = result.register
    should_return = result.should_return
    append = elements.append

    for nelement in node.elements:
        append(register(visit(nelement, context)))
        if should_return():
            return result

    return result.success(elements)

def visit_TupleNode(node, context):
    result = PysRunTimeResult()

    elements = []

    register = result.register
    should_return = result.should_return
    append = elements.append

    for nelement in node.elements:
        append(register(visit(nelement, context)))
        if should_return():
            return result

    return result.success(tuple(elements))

def visit_IdentifierNode(node, context):
    result = PysRunTimeResult()

    position = node.position
    name = node.token.value
    symbol_table = context.symbol_table

    with handle_exception(result, context, position):
        value = symbol_table.get(name)

        if value is undefined:
            closest_symbol = find_closest(symbol_table, name)

            return result.failure(
                PysException(
                    NameError(
                        f"name {name!r} is not defined" +
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
        if value == KW__DEBUG__ else
        KEYWORDS_TO_VALUES_MAP[value]
    )

def visit_AttributeNode(node, context):
    result = PysRunTimeResult()

    should_return = result.should_return
    nattribute = node.attribute

    target = result.register(visit(node.target, context))
    if should_return():
        return result

    with handle_exception(result, context, nattribute.position):
        return result.success(getattr(target, nattribute.value))

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

def visit_CallNode(node, context):
    result = PysRunTimeResult()

    args = []
    kwargs = {}

    register = result.register
    should_return = result.should_return
    append = args.append
    setitem = kwargs.__setitem__
    nposition = node.position

    target = register(visit(node.target, context))
    if should_return():
        return result

    for nargument in node.arguments:

        if isinstance(nargument, tuple):
            keyword, nvalue = nargument
            setitem(keyword.value, register(visit(nvalue, context)))
            if should_return():
                return result

        else:
            append(register(visit(nargument, context)))
            if should_return():
                return result

    with handle_exception(result, context, nposition):
        handle_call(target, context, nposition)
        return result.success(target(*args, **kwargs))

    if should_return():
        return result

def visit_ChainOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    nposition = node.position
    nexpressions = node.expressions

    left = register(visit(nexpressions[0], context))
    if should_return():
        return result

    with handle_exception(result, context, nposition):

        for i, toperand in enumerate(node.operations):
            omatch = toperand.match
            otype = toperand.type

            right = register(visit(nexpressions[i + 1], context))
            if should_return():
                return result

            if omatch(T_KEYWORD, KW_IN):
                value = left in right
            elif omatch(T_KEYWORD, KW_IS):
                value = left is right
            elif otype == T_CE:
                handle_call(ce, context, nposition)
                value = ce(left, right)
            elif otype == T_NCE:
                handle_call(nce, context, nposition)
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
        return result.success(register(visit(node.valid if condition else node.invalid, context)))

    if should_return():
        return result

def visit_BinaryOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    omatch = node.operand.match
    otype = node.operand.type

    left = register(visit(node.left, context))
    if should_return():
        return result

    with handle_exception(result, context, node.position):
        should_return_right = True

        if omatch(T_KEYWORD, KW_AND) or otype == T_AND:
            if not left:
                return result.success(left)
        elif omatch(T_KEYWORD, KW_OR) or otype == T_OR:
            if left:
                return result.success(left)
        elif otype == T_NULLISH:
            if left is not None:
                return result.success(left)
        else:
            should_return_right = False

        right = register(visit(node.right, context))
        if should_return():
            return result

        return result.success(
            right
            if should_return_right else
            BINARY_FUNCTIONS_MAP[otype](left, right)
        )

    if should_return():
        return result

def visit_UnaryOperatorNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    nposition = node.position
    otype = node.operand.type

    value = register(visit(node.value, context))
    if should_return():
        return result

    with handle_exception(result, context, nposition):

        if node.operand.match(T_KEYWORD, KW_NOT) or otype == T_NOT:
            return result.success(not value)

        elif is_incremental(otype):
            func = increment if otype == T_INCREMENT else decrement

            handle_call(func, context, nposition)
            increast_value = func(value)

            if node.operand_position == 'left':
                value = increast_value

            register(visit_declaration_AssignNode(node.value, context, increast_value))
            if should_return():
                return result

            return result.success(value)

        return result.success(UNARY_FUNCTIONS_MAP[otype](value))

    if should_return():
        return result

def visit_StatementsNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    body = node.body

    if len(body) == 1:
        value = register(visit(body[0], context))
        if should_return():
            return result

        return result.success(value)

    for nelement in body:
        register(visit(nelement, context))
        if should_return():
            return result

    return result.success(None)

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
    npackages = node.packages
    tname, tas_name = node.name
    name_position = tname.position

    with handle_exception(result, context, name_position):
        name_module = tname.value
        file, extension = split_file_extension(name_module)

        if is_python_extensions(extension):
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
                except ImportError:
                    use_python_package = True

        if use_python_package:
            pyimport = get_symbol('pyimport')

            if pyimport is undefined:
                pyimport = get_symbol('__import__')

                if pyimport is undefined:
                    return result.failure(
                        PysException(
                            NameError("names 'require', 'pyimport', and '__import__' is not defined"),
                            context,
                            node.position
                        )
                    )

            handle_call(pyimport, context, name_position)
            module = pyimport(name_module)

    if should_return():
        return result

    if npackages == 'all':

        with handle_exception(result, context, name_position):
            for package in getattr(
                module, '__all__',
                (package for package in dir(module) if not package.startswith('_'))
            ):
                set_symbol(package, getattr(module, package))

        if should_return():
            return result

    elif npackages:

        for tpackage, tas_package in npackages:

            with handle_exception(result, context, tpackage.position):
                set_symbol(
                    (tpackage if tas_package is None else tas_package).value,
                    getattr(module, tpackage.value)
                )

            if should_return():
                return result

    elif not (tname.type == T_STRING and tas_name is None):

        with handle_exception(result, context, node.position):
            set_symbol((tname if tas_name is None else tas_name).value, module)

        if should_return():
            return result

    return result.success(None)

def visit_IfNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    else_body = node.else_body

    for ncondition, body in node.cases_body:
        condition = register(visit(ncondition, context))
        if should_return():
            return result

        with handle_exception(result, context, ncondition.position):
            condition = True if condition else False

        if should_return():
            return result

        if condition:
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

    for ncondition, body in node.case_cases:
        case = register(visit(ncondition, context))
        if should_return():
            return result

        with handle_exception(result, context, ncondition.position):
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

        for (nerror_name, tparameter), body in node.catch_cases:

            if nerror_name:
                error_cls = register(visit_IdentifierNode(nerror_name, context))
                if result.error:
                    setimuattr(result.error, 'other', error)
                    break

                if not (isinstance(error_cls, type) and issubclass(error_cls, BaseException)):
                    return result.failure(
                        PysException(
                            TypeError("catching classes that do not inherit from BaseException is not allowed"),
                            context,
                            nerror_name.position,
                            error
                        )
                    )

            if nerror_name is None or is_object_of(exception, error_cls):

                if tparameter:

                    with handle_exception(result, context, tparameter.position):
                        context.symbol_table.set(tparameter.value, error.exception)

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
    nalias = node.alias

    context_value = register(visit(ncontext, context))
    if should_return():
        return result

    with handle_exception(result, context, ncontext_position):
        enter = getattr(context_value, '__enter__', undefined)
        exit = getattr(context_value, '__exit__', undefined)

        if enter is undefined:
            return result.failure(
                PysException(
                    TypeError(f"{type(context_value).__name__!r} object does not support the context manager protocol"),
                    context,
                    ncontext_position
                )
            )

        elif exit is undefined:
            return result.failure(
                PysException(
                    TypeError(
                        f"{type(context_value).__name__!r} object does not support the context manager protocol"
                        "(missed __exit__ method)"
                    ),
                    context,
                    ncontext_position
                )
            )

        handle_call(enter, context, ncontext_position)
        enter_value = enter()

    if should_return():
        return result

    if nalias:

        with handle_exception(result, context, nalias.position):
            context.symbol_table.set(nalias.value, enter_value)

        if should_return():
            return result

    register(visit(node.body, context))

    error = result.error

    with handle_exception(result, context, ncontext_position):
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
    nheader = node.header
    nheader_length = len(nheader)
    body = node.body
    else_body = node.else_body

    if nheader_length == 2:
        ndeclaration, niteration = nheader
        niteration_position = niteration.position

        iteration = register(visit(niteration, context))
        if should_return():
            return result

        with handle_exception(result, context, niteration_position):
            handle_call(getattr(iteration, '__iter__', None), context, niteration_position)
            iteration = iter(iteration)
            next = iteration.__next__

        if should_return():
            return result

        def condition():
            with handle_exception(result, context, niteration_position):
                handle_call(next, context, niteration_position)
                register(visit_declaration_AssignNode(ndeclaration, context, next()))

            if should_return():
                if is_object_of(result.error.exception, StopIteration):
                    result.error = None
                return False

            return True

        def update():
            pass

    elif nheader_length == 3:
        ndeclaration, ncondition, nupdate = nheader

        if ndeclaration:
            register(visit(ndeclaration, context))
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
    nposition = node.position
    name = node.name.value
    symbol_table = context.symbol_table

    for nbase in node.bases:
        append(register(visit(nbase, context)))
        if should_return():
            return result

    class_context = PysClassContext(
        name=name,
        symbol_table=PysClassSymbolTable(symbol_table),
        parent=context,
        parent_entry_position=nposition
    )

    register(visit(node.body, class_context))
    if should_return():
        return result

    with handle_exception(result, context, nposition):
        cls = type(name, tuple(bases), class_context.symbol_table.symbols)
        cls.__qualname__ = class_context.qualname

    if should_return():
        return result

    for ndecorator in reversed(node.decorators):
        decorator = register(visit(ndecorator, context))
        if should_return():
            return result

        with handle_exception(result, context, ndecorator.position):
            cls = decorator(cls)

        if should_return():
            return result

    with handle_exception(result, context, nposition):
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
    nposition = node.position
    name = node.name

    for nparameter in node.parameters:

        if isinstance(nparameter, tuple):
            keyword, nvalue = nparameter

            value = register(visit(nvalue, context))
            if should_return():
                return result

            append((keyword.value, value))

        else:
            append(nparameter.value)

    func = PysFunction(
        name=None if name is None else name.value,
        qualname=context.qualname,
        parameters=parameters,
        body=node.body,
        position=nposition,
        context=context
    )

    for ndecorator in reversed(node.decorators):
        decorator = register(visit(ndecorator, context))
        if should_return():
            return result

        with handle_exception(result, context, ndecorator.position):
            func = decorator(func)

        if should_return():
            return result

    if name:

        with handle_exception(result, context, nposition):
            context.symbol_table.set(name.value, func)

        if should_return():
            return result

    return result.success(func)

def visit_GlobalNode(node, context):
    context.symbol_table.globals.update(name.value for name in node.identifiers)
    return PysRunTimeResult().success(None)

def visit_ReturnNode(node, context):
    result = PysRunTimeResult()

    nvalue = node.value

    if nvalue:
        value = result.register(visit(nvalue, context))
        if result.should_return():
            return result

        return result.success_return(value)

    return result.success_return(None)

def visit_ThrowNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntarget = node.target
    nanother = node.another

    target = register(visit(ntarget, context))
    if should_return():
        return result

    if not is_object_of(target, BaseException):
        return result.failure(
            PysException(
                TypeError("exceptions must derive from BaseException"),
                context,
                ntarget.position
            )
        )

    if nanother:

        another = register(visit(nanother, context))
        if should_return():
            return result

        if not is_object_of(another, BaseException):
            return result.failure(
                PysException(
                    TypeError("exceptions must derive from BaseException"),
                    context,
                    nanother.position
                )
            )

        another = PysException(
            another,
            context,
            nanother.position
        )

    else:
        another = None

    return result.failure(
        PysException(
            target,
            context,
            node.position,
            another,
            bool(nanother)
        )
    )

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
                nmessage = node.message

                if nmessage:
                    message = register(visit(nmessage, context))
                    if should_return():
                        return result

                    return result.failure(
                        PysException(
                            AssertionError(message),
                            context,
                            node.position
                        )
                    )

                return result.failure(
                    PysException(
                        AssertionError,
                        context,
                        node.position
                    )
                )

        if should_return():
            return result

    return result.success(None)

def visit_DeleteNode(node, context):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    symbol_table = context.symbol_table

    for ntarget in node.targets:
        target_position = ntarget.position
        ntarget_type = ntarget.__class__

        if ntarget_type is PysIdentifierNode:
            name = ntarget.token.value

            with handle_exception(result, context, target_position):

                if not symbol_table.remove(name):
                    closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                    return result.failure(
                        PysException(
                            NameError(
                                (
                                    f"name {name!r} is not defined"
                                    if symbol_table.get(name) is undefined else
                                    f"name {name!r} is not defined on local"
                                )
                                +
                                (
                                    ''
                                    if closest_symbol is None else
                                    f". Did you mean {closest_symbol!r}?"
                                )
                            ),
                            context,
                            target_position
                        )
                    )

            if should_return():
                return result

        elif ntarget_type is PysAttributeNode:
            target = register(visit(ntarget.target, context))
            if should_return():
                return result

            with handle_exception(result, context, target_position):
                delattr(target, ntarget.attribute.value)

            if should_return():
                return result

        elif ntarget_type is PysSubscriptNode:
            target = register(visit(ntarget.target, context))
            if should_return():
                return result

            slice = register(visit_slice_SubscriptNode(ntarget.slice, context))
            if should_return():
                return result

            with handle_exception(result, context, target_position):
                del target[slice]

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
    ntype = node.__class__

    if ntype is slice:
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

    elif ntype is tuple:
        slices = []

        append = slices.append

        for element in node:
            append(register(visit_slice_SubscriptNode(element, context)))
            if should_return():
                return result

        return result.success(tuple(slices))

    else:
        value = register(visit(node, context))
        if should_return():
            return result

        return result.success(value)

def visit_declaration_AssignNode(node, context, value, operand=TOKENS['EQUAL']):
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntype = node.__class__

    if ntype is PysIdentifierNode:
        symbol_table = context.symbol_table
        name = node.token.value

        with handle_exception(result, context, node.position):

            if not symbol_table.set(name, value, operand=operand):
                closest_symbol = get_closest(symbol_table.symbols.keys(), name)

                result.failure(
                    PysException(
                        NameError(
                            (
                                f"name {name!r} is not defined"
                                if symbol_table.get(name) is undefined else
                                f"name {name!r} is not defined on local"
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

    elif ntype is PysAttributeNode:
        target = register(visit(node.target, context))
        if should_return():
            return result

        attribute = node.attribute.value

        with handle_exception(result, context, node.position):
            setattr(
                target,
                attribute,
                value if is_equals(operand) else BINARY_FUNCTIONS_MAP[operand](getattr(target, attribute), value)
            )

        if should_return():
            return result

    elif ntype is PysSubscriptNode:
        target = register(visit(node.target, context))
        if should_return():
            return result

        slice = register(visit_slice_SubscriptNode(node.slice, context))
        if should_return():
            return result

        with handle_exception(result, context, node.position):
            target[slice] = value if is_equals(operand) else BINARY_FUNCTIONS_MAP[operand](target[slice], value)

        if should_return():
            return result

    elif is_assign(ntype):
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