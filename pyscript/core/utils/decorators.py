from ..bases import Pys
from ..constants import ENV_PYSCRIPT_NO_TYPECHECK
from .generic import is_environ

from types import MethodType

class _PysNameSpaceUtilities(Pys):

    __slots__ = ()

    def __new__(cls):
        raise TypeError("cannot create namespace class instances")

    def new_singleton(cls, *args, **kwargs):
        # circular import problem solved
        from ..cache import pys_sys
        singletons = pys_sys.singletons
        if type(singletons.get(cls, None)) is not cls:
            singletons[cls] = cls.__new_singleton__(cls, *args, **kwargs)
        return singletons[cls]

    def readonly_attribute(*args, **kwargs):
        raise AttributeError("readonly attribute")

    def inheritable_class(cls, *args, **kwargs):
        raise TypeError(f"uninherited class for {cls.__name__}")

TYPECHECK_STACK = 0
BEARTYPE = False

def typecheck(func, *args, **kwargs):
    return func

if not is_environ(ENV_PYSCRIPT_NO_TYPECHECK):
    try:
        from beartype import beartype as typecheck
        TYPECHECK_STACK += 1
        BEARTYPE = True
    except:
        pass

def immutable(cls):
    cls.__setattr__ = _PysNameSpaceUtilities.readonly_attribute
    cls.__delattr__ = _PysNameSpaceUtilities.readonly_attribute
    return cls

def inheritable(cls):
    cls.__init_subclass__ = MethodType(_PysNameSpaceUtilities.inheritable_class, cls)
    return cls

def singleton(cls):
    cls.__new__ = _PysNameSpaceUtilities.new_singleton
    if not hasattr(cls, '__new_singleton__'):
        cls.__new_singleton__ = super(cls, cls).__new__
    return cls