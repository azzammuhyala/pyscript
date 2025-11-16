from .buffer import PysFileBuffer
from .cache import loading_modules, modules, library, undefined
from .constants import LIBRARY_PATH
from .exceptions import PysShouldReturn
from .handlers import handle_call
from .objects import PysModule, PysPythonFunction
from .results import PysRunTimeResult
from .symtab import build_symbol_table
from .utils.constants import BLACKLIST_PYTHON_BUILTINS
from .utils.general import (
    tostr,
    normalize_path,
    is_object_of as isobjectof
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

def _supported_method(pyfunc, object, name, *args, **kwargs):

    method = getattr(object, name, undefined)
    if method is undefined:
        return False, None

    if callable(method):
        code = pyfunc.__code__
        handle_call(method, code.context, code.position)

        try:
            result = method(*args, **kwargs)
            if result is NotImplemented:
                return False, None
            return True, result
        except NotImplementedError:
            return False, None

    return False, None

class _Printer:

    def __init__(self, name, text):
        self.name = name
        self.text = text

    def __repr__(self):
        return f'Type {self.name}() to see the full information text.'

    def __call__(self):
        print(self.text)

class _Helper(_Printer):

    def __init__(self):
        super().__init__('help', None)

    def __repr__(self):
        return f'Type {self.name}() for interactive help, or {self.name}(object) for help about object.'

    def __call__(self, *args, **kwargs):
        if not (args or kwargs):
            print(
                "Welcome to the PyScript programming language! "
                "This is the help utility directly to the Python help.\n\n"
                "To get help on a specific object, type 'help(object)'.\n"
                "To get the list of built-in functions, types, exceptions, and other objects, "
                "type 'help(\"builtins\")'."
            )
        else:
            return builtins.help(*args, **kwargs)

license = _Printer(
    'license',

    "MIT License - PyScript created by AzzamMuhyala.\n"
    "This language was written as a project and learning how language is works.\n"
    "For more information see on https://github.com/azzammuhyala/pyscript."
)

help = _Helper()

@PysPythonFunction
def require(pyfunc, name):
    name = tostr(name)

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
            f"cannot import module name {module_name!r} "
            f"from partially initialized module {pyfunc.__code__.context.file.name!r}, mostly during circular import"
        )

    loading_modules.add(path)

    try:

        package = modules.get(path, None)

        if package is None:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    file = PysFileBuffer(file.read(), path)
            except FileNotFoundError:
                raise ModuleNotFoundError(f"No module named {module_name!r}")
            except BaseException as e:
                raise ImportError(f"Cannot import module named {module_name!r}: {e}")

            symtab = build_symbol_table(file)

            package = PysModule('')
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

            modules[path] = package

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
        symbol_table=pyfunc.__code__.context.symbol_table
                     if globals is None else
                     build_symbol_table(file, globals),
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
        symbol_table=pyfunc.__code__.context.symbol_table
                     if globals is None else
                     build_symbol_table(file, globals),
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

    success, result = _supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = _supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            raise TypeError(
                f"unsupported operand type(s) for ~= or ce(): {type(a).__name__!r} and {type(b).__name__!r}"
            )

    return result

@PysPythonFunction
def nce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return not isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = _supported_method(pyfunc, a, '__nce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = _supported_method(pyfunc, b, '__nce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            success, result = _supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not success:
                success, result = _supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
                if not success:
                    raise TypeError(
                        f"unsupported operand type(s) for ~! or nce(): {type(a).__name__!r} and {type(b).__name__!r}"
                    )

            result = not result

    return result

@PysPythonFunction
def increment(pyfunc, object):
    if isinstance(object, (int, float)):
        return object + 1

    success, result = _supported_method(pyfunc, object, '__increment__')
    if not success:
        raise TypeError(f"bad operand type for unary ++ or increment(): {type(object).__name__!r}")

    return result

@PysPythonFunction
def decrement(pyfunc, object):
    if isinstance(object, (int, float)):
        return object - 1

    success, result = _supported_method(pyfunc, object, '__decrement__')
    if not success:
        raise TypeError(f"bad operand type for unary -- or decrement(): {type(object).__name__!r}")

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
    if not (name.startswith('_') or name in BLACKLIST_PYTHON_BUILTINS)
)

pys_builtins.__file__ = __file__
pys_builtins.license = license
pys_builtins.help = help
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