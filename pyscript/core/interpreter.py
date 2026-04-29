# Tree-Walk Interpreter

from .constants import DEBUG
from .cache import undefined
from .checks import is_sequence, is_equal, is_public_attribute
from .context import PysContext, PysClassContext
from .exceptions import PysTraceback
from .handlers import handle_call
from .mapping import GET_BINARY_FUNCTION, GET_UNARY_FUNCTION
from .nodes import *
from .pysbuiltins import ce, nce, increment, decrement
from .pystypes import PysFunction
from .results import PysRunTimeResult
from .symtab import PysClassSymbolTable, find_closest
from .token import TOKENS
from .utils.debug import get_traceback_info
from .utils.generic import getattribute, setimuattr, dkeys, is_object_of
from .utils.similarity import get_closest

from collections.abc import Iterable
from typing import Any, Callable

T_KEYWORD = TOKENS['KEYWORD']
T_STRING = TOKENS['STRING']
T_NOT = TOKENS['EXCLAMATION']
T_AND = TOKENS['DOUBLE_AMPERSAND']
T_NULLISH = TOKENS['DOUBLE_QUESTION']
T_OR = TOKENS['DOUBLE_PIPE']
T_CE = TOKENS['EQUAL_TILDE']
T_NCE = TOKENS['EXCLAMATION_TILDE']

get_incremental_function = {
    TOKENS['DOUBLE_PLUS']: increment,
    TOKENS['DOUBLE_MINUS']: decrement
}.__getitem__

get_value_from_keyword = {
    'True': True,
    'False': False,
    'None': None,
    'true': True,
    'false': False,
    'nil': None,
    'none': None,
    'null': None
}.__getitem__

def visit_NumberNode(node: PysNumberNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success(node.value.value)

def visit_StringNode(node: PysStringNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success(node.value.value)

def visit_KeywordNode(node: PysKeywordNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success(get_value_from_keyword(node.name.value))

def visit_DebugNode(node: PysDebugNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success(True if context.flags & DEBUG else False)

def visit_IdentifierNode(node: PysIdentifierNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    result._position = position = node.position
    name = node.name.value
    symbol_table = context.symbol_table

    with result:
        value = symbol_table.get(name)

        if value is undefined:
            closest_symbol = find_closest(symbol_table, name)

            return result.failure(
                PysTraceback(
                    NameError(
                        f"name {name!r} is not defined" +
                        ('' if closest_symbol is None else f". Did you mean {closest_symbol!r}?")
                    ),
                    context,
                    position
                )
            )

        return result.success(value)

    return result

def visit_DictionaryNode(node: PysDictionaryNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    elements = node.class_type()

    result._context = context
    register = result.register
    should_return = result.should_return
    setitem = getattribute(elements, '__setitem__')

    for nkey, nvalue in node.pairs:
        key = register(get_visitor(nkey.__class__)(nkey, context))
        if should_return():
            return result

        value = register(get_visitor(nvalue.__class__)(nvalue, context))
        if should_return():
            return result

        result._position = nkey.position
        with result:
            setitem(key, value)

        if should_return():
            return result

    return result.success(elements)

def visit_SetNode(node: PysSetNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    elements = set()

    result._context = context
    register = result.register
    should_return = result.should_return
    add = elements.add

    for nelement in node.elements:
        result._position = nelement.position
        with result:
            add(register(get_visitor(nelement.__class__)(nelement, context)))

        if should_return():
            return result

    return result.success(elements)

def visit_ListNode(node: PysListNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    elements = []

    register = result.register
    should_return = result.should_return
    append = elements.append

    for nelement in node.elements:
        append(register(get_visitor(nelement.__class__)(nelement, context)))
        if should_return():
            return result

    return result.success(elements)

def visit_TupleNode(node: PysTupleNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    elements = []

    register = result.register
    should_return = result.should_return
    append = elements.append

    for nelement in node.elements:
        append(register(get_visitor(nelement.__class__)(nelement, context)))
        if should_return():
            return result

    return result.success(tuple(elements))

def visit_AttributeNode(node: PysAttributeNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    ntarget = node.target

    target = result.register(get_visitor(ntarget.__class__)(ntarget, context))
    if result.should_return():
        return result

    nattribute = node.attribute

    result._context = context
    result._position = nattribute.position
    with result:
        return result.success(getattr(target, nattribute.value))

    return result

def visit_SubscriptNode(node: PysSubscriptNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntarget = node.target

    target = register(get_visitor(ntarget.__class__)(ntarget, context))
    if should_return():
        return result

    slice = register(visit_slice_from_SubscriptNode(node.slice, context))
    if should_return():
        return result

    result._context = context
    result._position = node.position
    with result:
        return result.success(target[slice])

    return result

def visit_CallNode(node: PysCallNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntarget = node.target

    target = register(get_visitor(ntarget.__class__)(ntarget, context))
    if should_return():
        return result

    args = []
    kwargs = {}

    b_tuple = tuple
    add_arg = args.append
    add_kwarg = kwargs.__setitem__

    for nargument in node.arguments:

        if nargument.__class__ is b_tuple:
            keyword, nvalue = nargument
            add_kwarg(keyword.value, register(get_visitor(nvalue.__class__)(nvalue, context)))
            if should_return():
                return result

        else:
            add_arg(register(get_visitor(nargument.__class__)(nargument, context)))
            if should_return():
                return result

    result._context = context
    result._position = nposition = node.position
    with result:
        handle_call(target, context, nposition)
        return result.success(target(*args, **kwargs))

    return result

def visit_ChainOperatorNode(node: PysChainOperatorNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    get_expression = node.expressions.__getitem__

    first = get_expression(0)

    left = register(get_visitor(first.__class__)(first, context))
    if should_return():
        return result

    result._context = context
    result._position = nposition = node.position
    with result:

        for i, toperand in enumerate(node.operations, start=1):
            otype = toperand.type
            nexpression = get_expression(i)

            right = register(get_visitor(nexpression.__class__)(nexpression, context))
            if should_return():
                return result

            if otype == T_KEYWORD:
                ovalue = toperand.value
                if ovalue == 'in':
                    value = left in right
                elif ovalue == 'is':
                    value = left is right
            elif otype == T_CE:
                handle_call(ce, context, nposition)
                value = ce(left, right)
            elif otype == T_NCE:
                handle_call(nce, context, nposition)
                value = nce(left, right)
            else:
                value = GET_BINARY_FUNCTION(otype)(left, right)

            if not value:
                break

            left = right

        return result.success(value)

    return result

def visit_TernaryOperatorNode(node: PysTernaryOperatorNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ncondition = node.condition

    condition = register(get_visitor(ncondition.__class__)(ncondition, context))
    if should_return():
        return result

    result._context = context
    result._position = node.position
    with result:
        nvalue = node.valid if condition else node.invalid

        value = register(get_visitor(nvalue.__class__)(nvalue, context))
        if should_return():
            return result

        return result.success(value)

    return result

def visit_BinaryOperatorNode(node: PysBinaryOperatorNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    nleft = node.left

    left = register(get_visitor(nleft.__class__)(nleft, context))
    if should_return():
        return result

    toperand = node.operand
    otype = toperand.type

    result._context = context
    result._position = node.position
    with result:
        return_right = True

        if otype == T_KEYWORD:
            ovalue = toperand.value
            if ovalue == 'and':
                if not left: return result.success(left)
            elif ovalue == 'or':
                if left: return result.success(left)
        elif otype == T_AND:
            if not left: return result.success(left)
        elif otype == T_OR:
            if left: return result.success(left)
        elif otype == T_NULLISH:
            if left is not None: return result.success(left)
        else:
            return_right = False

        nright = node.right

        right = register(get_visitor(nright.__class__)(nright, context))
        if should_return():
            return result

        return result.success(right if return_right else GET_BINARY_FUNCTION(otype)(left, right))

    return result

def visit_UnaryOperatorNode(node: PysUnaryOperatorNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    nvalue = node.value

    value = result.register(get_visitor(nvalue.__class__)(nvalue, context))
    if result.should_return():
        return result

    toperand = node.operand
    otype = toperand.type

    result._context = context
    result._position = node.position
    with result:

        if otype == T_KEYWORD:
            ovalue = toperand.value
            if ovalue == 'not':
                return result.success(not value)
            elif ovalue == 'typeof':
                return result.success(type(value).__name__)

        return result.success(GET_UNARY_FUNCTION(otype)(value))

    return result

def visit_IncrementalNode(node: PysIncrementalNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntarget = node.target

    value = register(get_visitor(ntarget.__class__)(ntarget, context))
    if should_return():
        return result

    result._context = context
    result._position = nposition = node.position
    with result:
        function = get_incremental_function(node.operand.type)
        handle_call(function, context, nposition)
        increast_value = function(value)

        if node.operand_position == 'left':
            value = increast_value

        register(visit_declaration_from_AssignmentNode(ntarget, context, increast_value))
        if should_return():
            return result

        return result.success(value)

    return result

def visit_StatementsNode(node: PysStatementsNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    body = node.body

    if len(body) == 1:
        nvalue = body[0]
        value = register(get_visitor(nvalue.__class__)(nvalue, context))
        if should_return():
            return result

        return result.success(value)

    for nelement in body:
        register(get_visitor(nelement.__class__)(nelement, context))
        if should_return():
            return result

    return result.success(None)

def visit_AssignmentNode(node: PysAssignmentNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    nvalue = node.value

    value = register(get_visitor(nvalue.__class__)(nvalue, context))
    if should_return():
        return result

    register(visit_declaration_from_AssignmentNode(node.target, context, value, node.operand.type))
    if should_return():
        return result

    return result.success(value)

def visit_ImportNode(node: PysImportNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    symbol_table = context.symbol_table
    get_symbol = symbol_table.get
    tname, tas_name = node.name

    result._context = context
    result._position = name_position = tname.position
    with result:
        name_module = tname.value
        use_python_package = False

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
                        PysTraceback(
                            NameError("names 'require', 'pyimport', and '__import__' is not defined"),
                            context,
                            node.position
                        )
                    )

            handle_call(pyimport, context, name_position)
            module = pyimport(name_module)

    should_return = result.should_return
    set_symbol = symbol_table.set
    npackages = node.packages

    if should_return():
        return result

    if npackages == 'all':

        with result:
            exported_from = '__all__'
            exported_packages = getattr(module, exported_from, undefined)
            if exported_packages is undefined:
                exported_from = '__dir__()'
                exported_packages = filter(is_public_attribute, dir(module))

            b_isinstance = isinstance
            b_getattr = getattr
            b_str = str

            for package in exported_packages:

                if not b_isinstance(package, b_str):
                    return result.failure(
                        PysTraceback(
                            TypeError(
                                f"Item in {module.__name__}.{exported_from} must be str, not {type(package).__name__}"
                            ),
                            context,
                            name_position
                        )
                    )

                set_symbol(package, b_getattr(module, package))

        if should_return():
            return result

    elif npackages:
        b_getattr = getattr

        for tpackage, tas_package in npackages:
            result._position = tpackage.position
            with result:
                set_symbol((tpackage if tas_package is None else tas_package).value, b_getattr(module, tpackage.value))
            if should_return():
                return result

    elif not (tname.type == T_STRING and tas_name is None):

        with result:
            set_symbol((tname if tas_name is None else tas_name).value, module)
        if should_return():
            return result

    return result.success(None)

def visit_IfNode(node: PysIfNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return

    for ncondition, body in node.cases_body:
        condition = register(get_visitor(ncondition.__class__)(ncondition, context))
        if should_return():
            return result

        result._position = ncondition.position
        with result:
            if condition:
                register(get_visitor(body.__class__)(body, context))
                return result if should_return() else result.success(None)

        if should_return():
            return result

    else_body = node.else_body

    if else_body:
        register(get_visitor(else_body.__class__)(else_body, context))
        if should_return():
            return result

    return result.success(None)

def visit_SwitchNode(node: PysSwitchNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ntarget = node.target

    fall_through = False
    no_match_found = True

    target = register(get_visitor(ntarget.__class__)(ntarget, context))
    if should_return():
        return result

    for ncondition, body in node.case_cases:

        if not fall_through:
            case = register(get_visitor(ncondition.__class__)(ncondition, context))
            if should_return():
                return result

        result._position = ncondition.position
        with result:

            if fall_through or target == case:
                fall_through = True
                no_match_found = False

                register(get_visitor(body.__class__)(body, context))
                if should_return():
                    if result.should_break:
                        result.should_break = False
                        fall_through = False
                    else:
                        return result

        if should_return():
            return result

    if (fall_through or no_match_found) and (default_body := node.default_body):
        register(get_visitor(default_body.__class__)(default_body, context))
        if should_return():
            if result.should_break:
                result.should_break = False
            else:
                return result

    return result.success(None)

def visit_MatchNode(node: PysMatchNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ntarget = node.target

    compare = False

    if ntarget:
        target = register(get_visitor(ntarget.__class__)(ntarget, context))
        if should_return():
            return result
        compare = True

    for ncondition, nvalue in node.cases:
        condition = register(get_visitor(ncondition.__class__)(ncondition, context))
        if should_return():
            return result

        result._position = ncondition.position
        with result:

            if target == condition if compare else (True if condition else False):
                value = register(get_visitor(nvalue.__class__)(nvalue, context))
                if should_return():
                    return result

                return result.success(value)

        if should_return():
            return result

    ndefault = node.default

    if ndefault:
        default = register(get_visitor(ndefault.__class__)(ndefault, context))
        if should_return():
            return result

        return result.success(default)

    return result.success(None)

def visit_TryNode(node: PysTryNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    body = node.body

    register(get_visitor(body.__class__)(body, context))

    should_return = result.should_return
    error = result.error

    if error:
        failure = result.failure
        exception = error.exception

        b_isinstance = isinstance
        b_issubclass = issubclass
        b_type = type
        b_BaseException = BaseException

        failure(None)

        for (targets, tparameter), body in node.catch_cases:
            handle_exception = True
            stop = False

            if targets:
                handle_exception = False

                for nerror_class in targets:
                    error_class = register(visit_IdentifierNode(nerror_class, context))
                    if result.error:
                        setimuattr(result.error, 'primary', error)
                        stop = True
                        break

                    if not (b_isinstance(error_class, b_type) and b_issubclass(error_class, b_BaseException)):
                        failure(
                            PysTraceback(
                                TypeError("catching classes that do not inherit from BaseException is not allowed"),
                                context,
                                nerror_class.position,
                                error
                            )
                        )
                        stop = True
                        break

                    if is_object_of(exception, error_class):
                        handle_exception = True
                        break

            if stop:
                break

            elif handle_exception:

                if tparameter:
                    result._context = context
                    result._position = tparameter.position
                    with result:
                        symbol_table = context.symbol_table
                        parameter = tparameter.value
                        symbol_table.set(parameter, error.exception)
                    if should_return():
                        break

                register(get_visitor(body.__class__)(body, context))
                if result.error:
                    setimuattr(result.error, 'primary', error)

                if tparameter:
                    with result:
                        symbol_table.remove(parameter)
                    if should_return():
                        break

                break

        else:
            failure(error)

    elif else_body := node.else_body:
        register(get_visitor(else_body.__class__)(else_body, context))

    finally_body = node.finally_body

    if finally_body:
        finally_result = PysRunTimeResult()
        finally_result.register(get_visitor(finally_body.__class__)(finally_body, context))
        if finally_result.should_return():
            if finally_result.error:
                setimuattr(finally_result.error, 'primary', result.error)
            return finally_result

    return result if should_return() else result.success(None)

def visit_WithNode(node: PysWithNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    exit_functions = []

    result._context = context
    register = result.register
    should_return = result.should_return
    append_exit_function = exit_functions.append
    set_symbol = context.symbol_table.set

    for ncontext, nalias in node.contexts:
        context_value = register(get_visitor(ncontext.__class__)(ncontext, context))
        if should_return():
            break

        result._position = ncontext_position = ncontext.position
        with result:
            enter = getattr(context_value, '__enter__', undefined)
            exit = getattr(context_value, '__exit__', undefined)

            missed_enter = enter is undefined
            missed_exit = exit is undefined

            if missed_enter or missed_exit:
                message = f"{type(context_value).__name__!r} object does not support the context manager protocol"

                if missed_enter and missed_exit:
                    pass
                elif missed_enter:
                    message += " (missed __enter__ method)"
                elif missed_exit:
                    message += " (missed __exit__ method)"

                result.failure(
                    PysTraceback(
                        TypeError(message),
                        context,
                        ncontext_position
                    )
                )
                break

            handle_call(enter, context, ncontext_position)
            enter_value = enter()
            append_exit_function((exit, ncontext_position))

        if should_return():
            break

        if nalias:
            result._position = nalias.position
            with result:
                set_symbol(nalias.value, enter_value)
            if should_return():
                break

    if not should_return():
        body = node.body
        register(get_visitor(body.__class__)(body, context))

    failure = result.failure
    error = result.error

    for exit, ncontext_position in reversed(exit_functions):
        result._position = ncontext_position
        with result:
            handle_call(exit, context, ncontext_position)
            if exit(*get_traceback_info(error)):
                failure(None)
                error = None

    if should_return():
        if result.error and result.error is not error:
            setimuattr(result.error, 'primary', error)
        return result

    return result.success(None)

def visit_ForNode(node: PysForNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    nheader = node.header
    nheader_length = len(nheader)

    if nheader_length == 2:
        ndeclaration, niteration = nheader

        iteration = register(get_visitor(niteration.__class__)(niteration, context))
        if should_return():
            return result

        result._position = niteration_position = niteration.position
        with result:
            handle_call(getattr(iteration, '__iter__', None), context, niteration_position)
            next = iter(iteration).__next__

        if should_return():
            return result

        b_StopIteration = StopIteration

        def condition():
            with result:
                handle_call(next, context, niteration_position)
                register(visit_declaration_from_AssignmentNode(ndeclaration, context, next()))
            if should_return():
                error = result.error
                if error and is_object_of(error.exception, b_StopIteration):
                    result.failure(None)
                return False
            return True

        def update():
            pass

    elif nheader_length == 3:
        ndeclaration, ncondition, nupdate = nheader

        if ndeclaration:
            register(get_visitor(ndeclaration.__class__)(ndeclaration, context))
            if should_return():
                return result

        if ncondition:
            ncondition_class = ncondition.__class__
            result._position = ncondition.position
            def condition():
                value = register(get_visitor(ncondition_class)(ncondition, context))
                if should_return():
                    return False
                with result:
                    return True if value else False

        else:
            def condition():
                return True

        if nupdate:
            nupdate_class = nupdate.__class__
            def update():
                register(get_visitor(nupdate_class)(nupdate, context))

        else:
            def update():
                pass

    body = node.body
    body_class = body.__class__

    while True:
        done = condition()
        if should_return():
            return result

        if not done:
            break

        register(get_visitor(body_class)(body, context))
        if should_return():
            if result.should_continue:
                result.should_continue = False
            elif result.should_break:
                break
            else:
                return result

        update()
        if should_return():
            return result

    if result.should_break:
        result.should_break = False

    elif else_body := node.else_body:
        register(get_visitor(else_body.__class__)(else_body, context))
        if should_return():
            return result

    return result.success(None)

def visit_WhileNode(node: PysWhileNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ncondition = node.condition
    ncondition_class = ncondition.__class__
    result._position = ncondition.position
    body = node.body
    body_class = body.__class__

    while True:
        condition = register(get_visitor(ncondition_class)(ncondition, context))
        if should_return():
            return result

        with result:
            if not condition:
                break

        if should_return():
            return result

        register(get_visitor(body_class)(body, context))
        if should_return():
            if result.should_continue:
                result.should_continue = False
            elif result.should_break:
                break
            else:
                return result

    if result.should_break:
        result.should_break = False

    elif else_body := node.else_body:
        register(get_visitor(else_body.__class__)(else_body, context))
        if should_return():
            return result

    return result.success(None)

def visit_DoWhileNode(node: PysDoWhileNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ncondition = node.condition
    result._position = ncondition.position
    ncondition_class = ncondition.__class__
    body = node.body
    body_class = body.__class__

    while True:
        register(get_visitor(body_class)(body, context))
        if should_return():
            if result.should_continue:
                result.should_continue = False
            elif result.should_break:
                break
            else:
                return result

        condition = register(get_visitor(ncondition_class)(ncondition, context))
        if should_return():
            return result

        with result:
            if not condition:
                break

        if should_return():
            return result

    if result.should_break:
        result.should_break = False

    elif else_body := node.else_body:
        register(get_visitor(else_body.__class__)(else_body, context))
        if should_return():
            return result

    return result.success(None)

def visit_RepeatNode(node: PysRepeatNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ncondition = node.condition
    result._position = ncondition.position
    ncondition_class = ncondition.__class__
    body = node.body

    if body:
        body_class = body.__class__

        while True:
            register(get_visitor(body_class)(body, context))
            if should_return():
                if result.should_continue:
                    result.should_continue = False
                elif result.should_break:
                    break
                else:
                    return result

            condition = register(get_visitor(ncondition_class)(ncondition, context))
            if should_return():
                return result

            with result:
                if condition:
                    break

            if should_return():
                return result

        if result.should_break:
            result.should_break = False

        elif else_body := node.else_body:
            register(get_visitor(else_body.__class__)(else_body, context))
            if should_return():
                return result

    else:

        while True:
            condition = register(get_visitor(ncondition_class)(ncondition, context))
            if should_return():
                return result

            with result:
                if condition:
                    break

            if should_return():
                return result

    return result.success(None)

def visit_ClassNode(node: PysClassNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    bases = []

    register = result.register
    should_return = result.should_return
    add_base = bases.append

    for nbase in node.bases:
        add_base(register(get_visitor(nbase.__class__)(nbase, context)))
        if should_return():
            return result

    nposition = node.position
    name = node.name.value
    symbol_table = context.symbol_table

    class_context = PysClassContext(
        name=name,
        symbol_table=PysClassSymbolTable(symbol_table),
        parent=context,
        parent_entry_position=nposition
    )

    body = node.body
    register(get_visitor(body.__class__)(body, class_context))
    if should_return():
        return result

    result._context = context
    result._position = nposition
    with result:
        cls = type(name, tuple(bases), class_context.symbol_table.symbols)
        cls.__qualname__ = class_context.qualname
        cls.__module__ = 'pyscript'

    if should_return():
        return result

    for ndecorator in reversed(node.decorators):
        decorator = register(get_visitor(ndecorator.__class__)(ndecorator, context))
        if should_return():
            return result

        result._position = dposition = ndecorator.position
        with result:
            handle_call(decorator, context, dposition)
            cls = decorator(cls)

        if should_return():
            return result

    result._position = nposition
    with result:
        symbol_table.set(name, cls)

    return result if should_return() else result.success(None)

def visit_FunctionNode(node: PysFunctionNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    parameters = []

    result._context = context
    register = result.register
    should_return = result.should_return
    add_parameter = parameters.append

    b_tuple = tuple

    for nparameter in node.parameters:

        if nparameter.__class__ is b_tuple:
            keyword, nvalue = nparameter

            value = register(get_visitor(nvalue.__class__)(nvalue, context))
            if should_return():
                return result

            add_parameter((keyword.value, value))

        else:
            add_parameter(nparameter.value)

    name = None if node.name is None else node.name.value
    nposition = node.position

    function = PysFunction(
        name=name,
        qualname=context.qualname,
        parameters=parameters,
        body=node.body,
        context=context,
        position=nposition
    )

    for ndecorator in reversed(node.decorators):
        decorator = register(get_visitor(ndecorator.__class__)(ndecorator, context))
        if should_return():
            return result

        result._position = dposition = ndecorator.position
        with result:
            handle_call(decorator, context, dposition)
            function = decorator(function)

        if should_return():
            return result

    if name:
        result._position = nposition
        with result:
            context.symbol_table.set(name, function)
        if should_return():
            return result

    return result.success(function)

def visit_GlobalNode(node: PysGlobalNode, context: PysContext) -> PysRunTimeResult:
    context.symbol_table.globals.update(name.value for name in node.identifiers)
    return PysRunTimeResult().success(None)

def visit_ReturnNode(node: PysReturnNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    nvalue = node.value

    if nvalue:
        value = result.register(get_visitor(nvalue.__class__)(nvalue, context))
        if result.should_return():
            return result

        return result.success_return(value)

    return result.success_return(None)

def visit_ThrowNode(node: PysThrowNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntarget = node.target

    target = register(get_visitor(ntarget.__class__)(ntarget, context))
    if should_return():
        return result

    b_BaseException = BaseException

    if not is_object_of(target, b_BaseException):
        return result.failure(
            PysTraceback(
                TypeError("exceptions must derive from BaseException"),
                context,
                ntarget.position
            )
        )

    nprimary = node.primary

    if nprimary:
        primary = register(get_visitor(nprimary.__class__)(nprimary, context))
        if should_return():
            return result

        if not is_object_of(primary, b_BaseException):
            return result.failure(
                PysTraceback(
                    TypeError("exceptions must derive from BaseException"),
                    context,
                    nprimary.position
                )
            )

        primary = PysTraceback(
            primary,
            context,
            nprimary.position
        )

    else:
        primary = None

    return result.failure(
        PysTraceback(
            target,
            context,
            node.position,
            primary,
            True if nprimary else False
        )
    )

def visit_AssertNode(node: PysAssertNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    if context.flags & DEBUG:
        return result.success(None)

    register = result.register
    should_return = result.should_return
    ncondition = node.condition

    condition = register(get_visitor(ncondition.__class__)(ncondition, context))
    if should_return():
        return result

    result._context = context
    result._position = ncondition.position
    with result:

        if not condition:
            nmessage = node.message

            if nmessage:
                message = register(get_visitor(nmessage.__class__)(nmessage, context))
                if should_return():
                    return result

                return result.failure(
                    PysTraceback(
                        AssertionError(message),
                        context,
                        node.position
                    )
                )

            return result.failure(
                PysTraceback(
                    AssertionError,
                    context,
                    node.position
                )
            )

        return result.success(None)

    return result

def visit_DeleteNode(node: PysDeleteNode, context: PysContext) -> PysRunTimeResult:
    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    symbol_table = context.symbol_table

    for ntarget in node.targets:
        ntarget_type = ntarget.__class__

        if ntarget_type is PysIdentifierNode:
            name = ntarget.name.value

            result._position = target_position = ntarget.position
            with result:

                if not symbol_table.remove(name):
                    closest_symbol = get_closest(dkeys(symbol_table.symbols), name)

                    return result.failure(
                        PysTraceback(
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
            tntarget = ntarget.target
            target = register(get_visitor(tntarget.__class__)(tntarget, context))
            if should_return():
                return result

            result._position = ntarget.position
            with result:
                delattr(target, ntarget.attribute.value)

            if should_return():
                return result

        elif ntarget_type is PysSubscriptNode:
            tntarget = ntarget.target
            target = register(get_visitor(tntarget.__class__)(tntarget, context))
            if should_return():
                return result

            slice = register(visit_slice_from_SubscriptNode(ntarget.slice, context))
            if should_return():
                return result

            result._position = ntarget.position
            with result:
                del target[slice]

            if should_return():
                return result

    return result.success(None)

def visit_EllipsisNode(node: PysEllipsisNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success(...)

def visit_ContinueNode(node: PysContinueNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success_continue()

def visit_BreakNode(node: PysBreakNode, context: PysContext) -> PysRunTimeResult:
    return PysRunTimeResult().success_break()

def visit_slice_from_SubscriptNode(
    node: PysNode | slice | tuple[PysNode | slice, ...],
    context: PysContext
) -> PysRunTimeResult:

    result = PysRunTimeResult()

    register = result.register
    should_return = result.should_return
    ntype = node.__class__

    if ntype is slice:
        start = node.start
        if start is not None:
            start = register(get_visitor(start.__class__)(start, context))
            if should_return():
                return result

        stop = node.stop
        if stop is not None:
            stop = register(get_visitor(stop.__class__)(stop, context))
            if should_return():
                return result

        step = node.step
        if step is not None:
            step = register(get_visitor(step.__class__)(step, context))
            if should_return():
                return result

        return result.success(slice(start, stop, step))

    elif ntype is tuple:
        indices = []
        add_indices = indices.append

        for element in node:
            add_indices(register(visit_slice_from_SubscriptNode(element, context)))
            if should_return():
                return result

        return result.success(tuple(indices))

    else:
        value = register(get_visitor(node.__class__)(node, context))
        if should_return():
            return result

        return result.success(value)

def visit_declaration_from_AssignmentNode(
    node: PysIdentifierNode | PysAttributeNode | PysSubscriptNode | PysSetNode | PysListNode | PysTupleNode,
    context: PysContext,
    value: Any,
    operand: int = TOKENS['EQUAL']
) -> PysRunTimeResult:

    result = PysRunTimeResult()

    result._context = context
    register = result.register
    should_return = result.should_return
    ntype = node.__class__

    if ntype is PysIdentifierNode:
        symbol_table = context.symbol_table
        name = node.name.value

        result._position = node.position
        with result:

            if not symbol_table.set(name, value, operand=operand):
                closest_symbol = get_closest(dkeys(symbol_table.symbols), name)

                result.failure(
                    PysTraceback(
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
        ntarget = node.target
        target = register(get_visitor(ntarget.__class__)(ntarget, context))
        if should_return():
            return result

        attribute = node.attribute.value

        result._position = node.position
        with result:
            setattr(
                target, attribute,
                value if is_equal(operand) else GET_BINARY_FUNCTION(operand)(getattr(target, attribute), value)
            )

        if should_return():
            return result

    elif ntype is PysSubscriptNode:
        ntarget = node.target
        target = register(get_visitor(ntarget.__class__)(ntarget, context))
        if should_return():
            return result

        slice = register(visit_slice_from_SubscriptNode(node.slice, context))
        if should_return():
            return result

        result._position = node.position
        with result:
            target[slice] = value if is_equal(operand) else GET_BINARY_FUNCTION(operand)(target[slice], value)

        if should_return():
            return result

    elif is_sequence(ntype):
        position = node.position

        if not isinstance(value, Iterable):
            return result.failure(
                PysTraceback(
                    TypeError(f"cannot unpack non-iterable {type(value).__name__} object"),
                    context,
                    position
                )
            )

        elements = node.elements
        count = 0

        result._position = position
        with result:

            for element, element_value in zip(elements, value):
                register(visit_declaration_from_AssignmentNode(element, context, element_value, operand))
                if should_return():
                    return result

                count += 1

        if should_return():
            return result

        length = len(elements)

        if count < length:
            return result.failure(
                PysTraceback(
                    ValueError(f"not enough values to unpack (expected {length}, got {count})"),
                    context,
                    node.position
                )
            )

        elif count > length:
            return result.failure(
                PysTraceback(
                    ValueError(f"to many values to unpack (expected {length})"),
                    context,
                    node.position
                )
            )

    return result.success(None)

get_visitor: Callable[[type[PysNode]], Callable[[PysNode, PysContext], PysRunTimeResult]] = {
    class_node: globals()['visit_' + class_node.__name__.removeprefix('Pys')]
    for class_node in PysNode.__subclasses__()
}.__getitem__