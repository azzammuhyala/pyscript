from .buffer import PysFileBuffer
from .cache import loading_modules, library, modules
from .constants import LIBRARY_PATH
from .exceptions import PysShouldReturn
from .objects import PysModule, PysPythonFunction
from .results import PysRunTimeResult
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
from os import getcwd
from os.path import (
    dirname as pdirname,
    join as pjoin,
    isdir as pisdir,
    exists as pexists,
    basename as pbasename
)

import builtins

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

@PysPythonFunction
def require(pyfunc, name):
    name = to_str(name)

    if name == '_pyscript':
        from .. import core
        return core

    elif name == 'builtins':
        return pys_builtins

    normalize = True

    if name in library:
        path = pjoin(LIBRARY_PATH, name)
        if not pisdir(path):
            path += '.pys'
        if pexists(path):
            normalize = False

    if normalize:
        path = normalize_path(
            pdirname(pyfunc.__code__.context.file.name) or getcwd(),
            name,
            absolute=False
        )

    module_name = pbasename(path)

    if pisdir(path):
        path = pjoin(path, '__init__.pys')

    if path in loading_modules:
        raise ImportError(
            "cannot import module name {!r} from partially initialized module {!r}, mostly during circular import"
            .format(module_name, pyfunc.__code__.context.file.name)
        )

    loading_modules.add(path)

    try:

        package = modules.get(path, None)

        if package is None:
            try:
                with open(path, 'r') as file:
                    file = PysFileBuffer(file.read(), path)
            except FileNotFoundError:
                raise ModuleNotFoundError("No module named {!r}".format(module_name))
            except BaseException as e:
                raise ImportError("Cannot import module named {!r}: {}".format(module_name, e))

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
                raise PysShouldReturn(PysRunTimeResult().failure(result.error))

        return package

    finally:
        if path in loading_modules:
            loading_modules.remove(path)

@PysPythonFunction
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

@PysPythonFunction
def locals(pyfunc):
    return pyfunc.__code__.context.symbol_table.symbols

@PysPythonFunction
def vars(pyfunc, object=None):
    if object is None:
        return pyfunc.__code__.context.symbol_table.symbols

    return builtins.vars(object)

@PysPythonFunction
def dir(pyfunc, *args):
    if len(args) == 0:
        return list(pyfunc.__code__.context.symbol_table.symbols.keys())

    return builtins.dir(*args)

@PysPythonFunction
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
        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

@PysPythonFunction
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
        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

    return result.value

@PysPythonFunction
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

@PysPythonFunction
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

@PysPythonFunction
def increment(pyfunc, object):
    if isinstance(object, (int, float)):
        return object + 1

    success, result = supported_method(pyfunc, object, '__increment__')
    if not success:
        raise TypeError("unsupported operand type(s) for ++ or increment(): {!r}".format(type(object).__name__))

    return result

@PysPythonFunction
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