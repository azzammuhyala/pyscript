from ..constants import PYSCRIPT_TYPECHECKING

from os import environ

def typechecked(func, *args, **kwargs):
    return func

if environ.get(PYSCRIPT_TYPECHECKING, '1') == '1':
    try:
        from beartype import beartype as typechecked
    except ImportError:
        try:
            from typeguard import typechecked
        except ImportError:
            environ[PYSCRIPT_TYPECHECKING] = '0'

class _Utilities:

    def new_singleton(cls, *args, **kwargs):
        from ..cache import singletons
        if type(singletons.get(cls, None)) is not cls:
            singletons[cls] = cls.__new_singleton__(cls, *args, **kwargs)
        return singletons[cls]

    def readonly_attribute(*args, **kwargs):
        raise AttributeError("readonly attribute")

    def inheritable_class(*args, **kwargs):
        raise TypeError("uninherited class")

def immutable(cls):
    cls.__setattr__ = _Utilities.readonly_attribute
    cls.__delattr__ = _Utilities.readonly_attribute
    return cls

def inheritable(cls):
    cls.__init_subclass__ = _Utilities.inheritable_class
    return cls

def singleton(cls):
    cls.__new__ = _Utilities.new_singleton
    if not hasattr(cls, '__new_singleton__'):
        cls.__new_singleton__ = super(cls, cls).__new__
    return cls