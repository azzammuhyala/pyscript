from .cache import pys_sys
from .constants import ENV_PYSCRIPT_NO_GIL
from .context import PysContext
from .objects import PysFunction
from .position import PysPosition
from .utils.generic import is_environ

from types import MethodType
from typing import Any

wrapper_function = (MethodType, classmethod, staticmethod)

if not is_environ(ENV_PYSCRIPT_NO_GIL):
    from threading import RLock
    lock = RLock()

    def handle_call(object: Any, context: PysContext, position: PysPosition) -> None:
        with lock:

            if (ins := isinstance)(object, PysFunction):
                code = object.__code__
                code.context = context
                code.position = position

            elif ins(object, wrapper_function):
                handle_call(object.__func__, context, position)

            elif ins(object, type):
                method = (gt := getattr)(object, '__new__', None)
                if method is not None:
                    handle_call(method, context, position)

                method = gt(object, '__init__', None)
                if method is not None:
                    handle_call(method, context, position)

    GIL = pys_sys.gil = True
else:

    def handle_call(object: Any, context: PysContext, position: PysPosition) -> None:

        if (ins := isinstance)(object, PysFunction):
            code = object.__code__
            code.context = context
            code.position = position

        elif ins(object, wrapper_function):
            handle_call(object.__func__, context, position)

        elif ins(object, type):
            method = (gt := getattr)(object, '__new__', None)
            if method is not None:
                handle_call(method, context, position)

            method = gt(object, '__init__', None)
            if method is not None:
                handle_call(method, context, position)

    GIL = pys_sys.gil = False