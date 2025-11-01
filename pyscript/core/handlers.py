from .exceptions import PysException, PysShouldReturn
from .objects import PysPythonFunction, PysFunction
from .position import PysPosition
from .results import PysRunTimeResult
from .utils import is_object_of, print_traceback

from . import cache

from types import MethodType

class handle_exception:

    __slots__ = ('result', 'context', 'position')

    def __init__(self, result, context, position):
        self.result = result
        self.context = context
        self.position = position

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False

        elif exc_type is PysShouldReturn:
            self.result.register(exc_val.result)
            return True

        self.result.failure(PysException(exc_type if exc_val is None else exc_val, self.context, self.position))
        return True

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
            method = getattr(object, call, None)
            if method is not None:
                handle_call(method, context, position)

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
            cache.hook.display(result.value)

    if result_runtime.should_return():
        if result_runtime.error:
            print_traceback(result_runtime.error)
        return 1

    return 0