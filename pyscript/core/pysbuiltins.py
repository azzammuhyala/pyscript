import builtins

def license():
    print("MIT License - PyScript created by AzzamMuhyala.")
    print("For more information see on https://github.com/azzammuhyala/pyscript")

def closeeq(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        from math import isclose
        return isclose(a, b)

    result = getattr(a, '__ce__', None)

    if not callable(result):
        raise TypeError("unsupported operand type(s) for close(): '" + type(a).__name__ + "'")

    return result(b)

def exec(string, globals=None):
    if not isinstance(string, str):
        raise TypeError("exec(): string must be str")
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("exec(): globals must be dict")

    from .runner import pys_exec

    pys_exec(string, globals)

def eval(string, globals=None):
    if not isinstance(string, str):
        raise TypeError("exec(): string must be str")
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("exec(): globals must be dict")

    from .runner import pys_eval

    return pys_eval(string, globals)

class generator:

    def __init__(self, init, wrap, exception=None):
        if not callable(wrap):
            raise TypeError("generator(): wrap must be callable")
        if not (exception is None or callable(exception)):
            raise TypeError("generator(): exception must be callable")

        self.init = init
        self.wrap = wrap
        self.exception = exception

    def __iter__(self):
        self.iter = iter(self.init)
        return self

    def __next__(self):
        while True:
            result = next(self.iter)
            if self.exception is None or self.exception(result):
                return self.wrap(result)

builtins_dict = {}

def _set(name, value):
    from .utils import SYNTAX
    builtins_dict[SYNTAX['builtins'].get(name, name)] = value

_set('pyimport', __import__)
_set('license', license)
_set('closeeq', closeeq)
_set('exec', exec)
_set('eval', eval)
_set('generator', generator)

for name in dir(builtins):
    if not (
        name.startswith('_') or
        name in {
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
    ):
        _set(name, getattr(builtins, name))

del _set