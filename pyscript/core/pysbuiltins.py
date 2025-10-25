from .buffer import PysFileBuffer
from .cache import loading_modules, library, modules
from .constants import LIBRARY_PATH
from .objects import PysModule, PysPythonFunction
from .symtab import build_symbol_table
from .utils import (
    builtins_blacklist,
    to_str,
    normalize_path,
    is_object_of as isobjectof,
    supported_method
)

from math import isclose
from importlib import import_module as pyimport

import builtins
import os

class _Printer:

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        return 'Type {}() to see the full information text.'.format(self.name)

    def __call__(self):
        print(self.text)

license = _Printer(
    'license',

    "MIT License - PyScript created by AzzamMuhyala.\n"
    "This language was written as a project and learning how language is works.\n"
    "For more information see on https://github.com/azzammuhyala/pyscript."
)

def require(pyfunc, name):
    name = to_str(name)
    dirname = os.path.dirname(pyfunc.__code__.context.file.name) or os.getcwd()

    if name == '_pyscript':
        from .. import core
        return core

    elif name == 'builtins':
        return pys_builtins

    elif name in library:
        path = os.path.join(LIBRARY_PATH, name)
        if not os.path.isdir(path):
            path += '.pys'
        if not os.path.exists(path):
            path = normalize_path(dirname, name, absolute=False)

    else:
        path = normalize_path(dirname, name, absolute=False)

    filename = os.path.basename(path)

    if os.path.isdir(path):
        path = os.path.join(path, '__init__.pys')

    if path in loading_modules:
        raise ImportError(
            "cannot import module name {!r} from partially initialized module {!r}, mostly during circular import"
            .format(filename, pyfunc.__code__.context.file.name)
        )

    loading_modules.add(path)

    try:
        package = modules.get(path, None)

        if package is None:
            try:
                with open(path, 'r') as file:
                    file = PysFileBuffer(file.read(), path)
            except FileNotFoundError:
                raise ModuleNotFoundError("No module named {!r}".format(filename))
            except BaseException as e:
                raise ImportError("Cannot import module named {!r}: {}".format(filename, e))

            symtab = build_symbol_table(file)

            modules[path] = package = PysModule('')
            package.__dict__ = symtab.symbols

            from .runner import pys_runner

            result = pys_runner(
                file=file,
                mode='exec',
                symbol_table=symtab,
                context_parent=pyfunc.__code__.context,
                context_parent_entry_position=pyfunc.__code__.position
            )

            if result.error:
                from .exceptions import PysShouldReturn
                from .results import PysRunTimeResult

                raise PysShouldReturn(PysRunTimeResult().failure(result.error))

        return package

    finally:
        if path in loading_modules:
            loading_modules.remove(path)

def globals(pyfunc):
    symbol_table = pyfunc.__code__.context.symbol_table.parent

    if symbol_table:
        result = {}

        while symbol_table:
            result |= symbol_table.symbols
            symbol_table = symbol_table.parent

        return result

    else:
        return pyfunc.__code__.context.symbol_table.symbols

def locals(pyfunc):
    return pyfunc.__code__.context.symbol_table.symbols

def vars(pyfunc, object=None):
    if object is None:
        return pyfunc.__code__.context.symbol_table.symbols

    return builtins.vars(object)

def dir(pyfunc, *args):
    if len(args) == 0:
        return list(pyfunc.__code__.context.symbol_table.symbols.keys())

    return builtins.dir(*args)

def exec(pyfunc, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("exec(): globals must be dict")

    file = PysFileBuffer(source, '<exec>')

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=pyfunc.__code__.context.symbol_table if globals is None else build_symbol_table(file, globals),
        context_parent=pyfunc.__code__.context,
        context_parent_entry_position=pyfunc.__code__.position
    )

    if result.error:
        from .exceptions import PysShouldReturn
        from .results import PysRunTimeResult

        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

def eval(pyfunc, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("eval(): globals must be dict")

    file = PysFileBuffer(source, '<eval>')

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='eval',
        symbol_table=pyfunc.__code__.context.symbol_table if globals is None else build_symbol_table(file, globals),
        context_parent=pyfunc.__code__.context,
        context_parent_entry_position=pyfunc.__code__.position
    )

    if result.error:
        from .exceptions import PysShouldReturn
        from .results import PysRunTimeResult

        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

    return result.value

def ce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)

    if not success:
        raise TypeError(
            "unsupported operand type(s) for ~= or ce(): {!r} and {!r}".format(
                type(a).__name__,
                type(b).__name__
            )
        )

    return result

def nce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return not isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = supported_method(pyfunc, a, '__nce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = supported_method(pyfunc, b, '__nce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            success, result = supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not success:
                success, result = supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
            result = not result

    if not success:
        raise TypeError(
            "unsupported operand type(s) for ~! or nce(): {!r} and {!r}".format(
                type(a).__name__,
                type(b).__name__
            )
        )

    return result

def increment(pyfunc, object):
    if isinstance(object, (int, float)):
        return object + 1

    success, result = supported_method(pyfunc, object, '__increment__')
    if not success:
        raise TypeError("unsupported operand type(s) for ++ or increment(): {!r}".format(type(object).__name__))

    return result

def decrement(pyfunc, object):
    if isinstance(object, (int, float)):
        return object - 1

    success, result = supported_method(pyfunc, object, '__decrement__')
    if not success:
        raise TypeError("unsupported operand type(s) for -- or decrement(): {!r}".format(type(object).__name__))

    return result

def comprehension(init, wrap, condition=None):
    if not callable(wrap):
        raise TypeError("comprehension(): wrap must be callable")
    if not (condition is None or callable(condition)):
        raise TypeError("comprehension(): condition must be callable")

    return map(wrap, init if condition is None else filter(condition, init))

require = PysPythonFunction(require)
globals = PysPythonFunction(globals)
locals = PysPythonFunction(locals)
vars = PysPythonFunction(vars)
dir = PysPythonFunction(dir)
exec = PysPythonFunction(exec)
eval = PysPythonFunction(eval)
ce = PysPythonFunction(ce)
nce = PysPythonFunction(nce)
increment = PysPythonFunction(increment)
decrement = PysPythonFunction(decrement)

pys_builtins = PysModule(
    'built-in',

    "Built-in functions, types, exceptions, and other objects.\n\n"
    "This module provides direct access to all 'built-in' identifiers of PyScript and Python."
)

pys_builtins.__dict__.update(
    (name, getattr(builtins, name))
    for name in builtins.dir(builtins)
    if not (name.startswith('_') or name in builtins_blacklist)
)

pys_builtins.__file__ = __file__
pys_builtins.license = license
pys_builtins.pyimport = pyimport
pys_builtins.require = require
pys_builtins.globals = globals
pys_builtins.locals = locals
pys_builtins.vars = vars
pys_builtins.dir = dir
pys_builtins.exec = exec
pys_builtins.eval = eval
pys_builtins.ce = ce
pys_builtins.nce = nce
pys_builtins.increment = increment
pys_builtins.decrement = decrement
pys_builtins.comprehension = comprehension
pys_builtins.isobjectof = isobjectof