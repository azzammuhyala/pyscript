from .cache import lock, hook
from .exceptions import PysException, PysShouldReturn
from .objects import PysPythonFunction, PysFunction
from .position import PysPosition
from .results import PysRunTimeResult
from .utils.constants import CONSTRUCTOR_METHODS
from .utils.debug import print_traceback
from .utils.general import get_error_args, is_object_of

from types import MethodType

class handle_exception:

    __slots__ = ('result', 'context', 'position')

    def __init__(self, result, context, position):
        self.result = result
        self.context = context
        self.position = position

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False

        self.result.register(exc_val.result) \
            if isinstance(exc_val, PysShouldReturn) else \
        self.result.failure(
            PysException(
                exc_type if exc_val is None else exc_val,
                self.context,
                self.position
            )
        )

        return True

def handle_call(object, context, position):
    with lock:

        if isinstance(object, PysFunction):
            code = object.__code__
            code.call_context = context
            code.position = position

        elif isinstance(object, PysPythonFunction):
            code = object.__code__
            code.context = context
            code.position = position

        elif isinstance(object, type):
            for call in CONSTRUCTOR_METHODS:
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
            if hook.exception is not None:
                hook.exception(*get_error_args(result.error))
            return 1

        elif hook.display is not None:
            hook.display(result.value)

    if result_runtime.should_return():
        if result_runtime.error:
            print_traceback(*get_error_args(result_runtime.error))
        return 1

    return 0