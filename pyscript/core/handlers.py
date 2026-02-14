from .constants import ENV_PYSCRIPT_NO_GIL
from .objects import PysFunction

from os import environ
from types import MethodType

wrapper_function = (MethodType, classmethod, staticmethod)

if environ.get(ENV_PYSCRIPT_NO_GIL) is None:
    from threading import RLock

    lock = RLock()

    def handle_call(object, context, position):
        with lock:
            ins = isinstance

            if ins(object, PysFunction):
                code = object.__code__
                code.context = context
                code.position = position

            elif ins(object, wrapper_function):
                handle_call(object.__func__, context, position)

            elif ins(object, type):
                gt = getattr

                method = gt(object, '__new__', None)
                if method is not None:
                    handle_call(method, context, position)

                method = gt(object, '__init__', None)
                if method is not None:
                    handle_call(method, context, position)

    GIL = True
else:

    def handle_call(object, context, position):
        ins = isinstance

        if ins(object, PysFunction):
            code = object.__code__
            code.context = context
            code.position = position

        elif ins(object, wrapper_function):
            handle_call(object.__func__, context, position)

        elif ins(object, type):
            gt = getattr

            method = gt(object, '__new__', None)
            if method is not None:
                handle_call(method, context, position)

            method = gt(object, '__init__', None)
            if method is not None:
                handle_call(method, context, position)

    GIL = False