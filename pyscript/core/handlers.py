from .cache import pys_sys
from .constants import SITE_PACKAGES_PATH, ENV_PYSCRIPT_WITH_GIL
from .context import PysContext
from .position import PysPosition
from .pystypes import PysFunction
from .utils.generic import is_environ

from site import ENABLE_USER_SITE
from types import MethodType
from typing import Any

import os

wrapper_function = (MethodType, classmethod, staticmethod)

if ENABLE_USER_SITE:
    try:
        if os.path.isfile(SITE_PACKAGES_PATH):
            os.remove(SITE_PACKAGES_PATH)
        if not os.path.exists(SITE_PACKAGES_PATH):
            os.mkdir(SITE_PACKAGES_PATH)
    except:
        pass

GIL = pys_sys.gil = False
if is_environ(ENV_PYSCRIPT_WITH_GIL):
    try:
        from threading import RLock
        gil_lock = RLock()
    except:
        pass
    else:
        GIL = pys_sys.gil = True

if GIL:
    def handle_call(object: Any, context: PysContext, position: PysPosition) -> None:
        with gil_lock:
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

else:
    def handle_call(object: Any, context: PysContext, position: PysPosition) -> None:
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