from .utils import SYNTAX

import builtins

_singleton_objects = {}

class UndefinedType:

    __slots__ = ()

    def __new__(cls):
        if _singleton_objects.get('undefined', None) is None:
            _singleton_objects['undefined'] = super().__new__(cls)
        return _singleton_objects['undefined']

    def __bool__(self):
        return False

    def __repr__(self):
        return 'undefined'

undefined = UndefinedType()

def license():
    print("MIT License - PyScript created by AzzamMuhyala.")
    print("For more information see on https://github.com/azzammuhyala/pyscript")

def closeeq(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        from math import isclose
        return isclose(a, b)

    result = getattr(a, '__ce__', None)

    if not callable(result):
        raise TypeError("bad operand type for close(): '" + type(a).__name__ + "'")

    return result(b)

def increment(x):
    if isinstance(x, (int, float, complex)):
        return x + 1

    result = getattr(x, '__increment__', None)

    if not callable(result):
        raise TypeError("bad operand type for increment(): '" + type(x).__name__ + "'")

    return result()

def decrement(x):
    if isinstance(x, (int, float, complex)):
        return x - 1

    result = getattr(x, '__decrement__', None)

    if not callable(result):
        raise TypeError("bad operand type for decrement(): '" + type(x).__name__ + "'")

    return result()

builtins_dict = {}

_builtins = SYNTAX['builtins']
_illegal_builtins = {
    'compile',
    'copyright',
    'credits',
    'eval',
    'exec',
    'globals',
    'help',
    'license',
    'locals'
}

builtins_dict[_builtins.get('true', 'true')] = True
builtins_dict[_builtins.get('false', 'false')] = False
builtins_dict[_builtins.get('none', 'none')] = None
builtins_dict[_builtins.get('undefined', 'undefined')] = undefined

builtins_dict[_builtins.get('pyimport', 'pyimport')] = __import__
builtins_dict[_builtins.get('license', 'license')] = license
builtins_dict[_builtins.get('closeeq', 'closeeq')] = closeeq
builtins_dict[_builtins.get('increment', 'increment')] = increment
builtins_dict[_builtins.get('decrement', 'decrement')] = decrement

for builtin in dir(builtins):
    if not (
        builtin.startswith('_') or
        builtin in _illegal_builtins
    ):
        builtins_dict[_builtins.get(builtin, builtin)] = getattr(builtins, builtin)