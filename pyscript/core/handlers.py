from .cache import lock, hook
from .constants import PYSCRIPT_GIL
from .exceptions import PysTraceback, PysSignal
from .objects import PysPythonFunction, PysFunction
from .position import PysPosition
from .results import PysRunTimeResult
from .utils.debug import print_traceback
from .utils.generic import get_error_args

from os import environ
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
        # return
        # ^^^^^^  <--- debug only

        if exc_type is not None:

            self.result.register(exc_val.result) \
            if exc_type is PysSignal else \
            self.result.failure(
                PysTraceback(
                    exc_type if exc_val is None else exc_val,
                    self.context,
                    self.position
                )
            )

        return True

if environ.get(PYSCRIPT_GIL, '1') == '1':

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
                method = getattr(object, '__new__', None)
                if method is not None:
                    handle_call(method, context, position)

                method = getattr(object, '__init__', None)
                if method is not None:
                    handle_call(method, context, position)

            elif isinstance(object, MethodType):
                handle_call(object.__func__, context, position)

else:

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
            method = getattr(object, '__new__', None)
            if method is not None:
                handle_call(method, context, position)

            method = getattr(object, '__init__', None)
            if method is not None:
                handle_call(method, context, position)

        elif isinstance(object, MethodType):
            handle_call(object.__func__, context, position)

def handle_execute(result):
    result_runtime = PysRunTimeResult()

    with handle_exception(result_runtime, result.context, PysPosition(result.context.file, -1, -1)):

        if result.error:
            if result.error.exception is SystemExit:
                return 0
            if type(result.error.exception) is SystemExit:
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