from .exceptions import PysException, PysShouldReturn
from .objects import PysPythonFunction, PysFunction
from .position import PysPosition
from .results import PysRunTimeResult
from .utils import is_object_of, print_traceback

from . import cache

from contextlib import contextmanager
from types import MethodType

@contextmanager
def handle_exception(result, context, position):
    try:
        yield
    except PysShouldReturn as e:
        result.register(e.result)
    except BaseException as e:
        result.failure(PysException(e, context, position))

def handle_call(object, context, position):
    if isinstance(object, PysFunction):
        code = object.__code__
        code.call_context = context
        code.position = position

    elif isinstance(object, PysPythonFunction):
        code = object.__code__
        code.context = context
        code.position = position

    elif isinstance(object, type):
        for call in ('__new__', '__init__'):
            handle_call(getattr(object, call, None), context, position)

    elif isinstance(object, MethodType):
        handle_call(object.__func__, context, position)

def handle_execute(result):
    result_runtime = PysRunTimeResult()

    with handle_exception(result_runtime, result.context, PysPosition(result.context.file, -1, -1)):

        if result.error:
            if is_object_of(result.error.exception, SystemExit):
                return result.error.exception.code
            if cache.hook.exception is not None:
                cache.hook.exception(result.error)
            return 1

        elif cache.hook.display is not None:
            if result.mode == 'exec' and len(result.value) == 1:
                cache.hook.display(result.value[0])
            elif result.mode == 'eval':
                cache.hook.display(result.value)

    if result_runtime.should_return():
        if result_runtime.error:
            print_traceback(result_runtime.error)
        return 1

    return 0