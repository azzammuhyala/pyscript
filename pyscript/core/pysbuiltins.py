from .bases import Pys
from .buffer import PysFileBuffer
from .cache import pys_sys
from .checks import is_blacklist_python_builtin, is_private_attribute
from .constants import OTHER_PATH, NO_COLOR, CLASSIC_LINE_SHELL, NO_COLOR_PROMPT
from .exceptions import PysSignal
from .handlers import handle_call
from .mapping import GET_ACOLOR
from .pystypes import PysFunction, PysPythonFunction, PysBuiltinFunction
from .results import PysRunTimeResult
from .shell import PysClassicLineShell, PysPromptToolkitLineShell, ADVANCE_LINE_SHELL_SUPPORT
from .symtab import new_module_namespace
from .utils.debug import import_readline
from .utils.generic import dkeys, get_sequence, is_object_of as isobjectof
from .utils.module import find_module_path, set_python_path, remove_python_path
from .utils.path import base, normpath
from .utils.string import normstr

from math import inf, nan, isclose
from importlib import import_module
from inspect import signature
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType, ModuleType, NoneType
from typing import Any, Callable

import builtins
import os
import sys

real_number = (int, float)
sequence = (list, tuple, set)
optional_mapping = (dict, NoneType)
static_wrapper_function = (staticmethod,)
wrapper_function = (MethodType, PysPythonFunction, classmethod)
python_function = (BuiltinFunctionType, BuiltinMethodType, FunctionType)

pyhelp = builtins.help
pyvars = builtins.vars
pydir = builtins.dir

def _supported_method(pyfunc: PysPythonFunction, object: Any, name: str, *args, **kwargs) -> tuple[bool, Any]:
    method = getattr(object, name, None)
    if callable(method):
        code = pyfunc.__code__
        handle_call(method, code.context, code.position)
        try:
            result = method(*args, **kwargs)
            if result is not NotImplemented:
                return True, result
        except NotImplementedError:
            pass
    return False, None

def _unpack_comprehension_function(pyfunc: PysPythonFunction, function: Callable) -> Callable:
    check = function
    final = function
    offset = 0

    if isinstance(function, wrapper_function):
        check = function.__func__
        offset += 1
    elif isinstance(function, static_wrapper_function):
        check = function.__func__

    if isinstance(check, PysFunction):
        length = max(check.__code__.parameters_length - offset, 0)
        if length == 0:
            def final(item):
                return function()
        elif length > 1:
            def final(item):
                return function(*item)

    elif isinstance(check, python_function):
        parameters = signature(check).parameters
        length = max(len(parameters) - offset, 0)
        if length == 0:
            def final(item):
                return function()
        elif length > 1 or any(p.kind == p.VAR_POSITIONAL for p in parameters.values()):
            def final(item):
                return function(*item)

    code = pyfunc.__code__
    handle_call(function, code.context, code.position)

    return final

class PysPrinter(Pys):

    def __init__(self, name: str, text: str | Any) -> None:
        self.name = name
        self.text = text

    def __repr__(self) -> str:
        return f'Type {self.name}() to see the full information text.'

    def __call__(self) -> None:
        print(self.text)

class PysHelper(PysPrinter):

    def __init__(self) -> None:
        super().__init__('help', None)

    def __repr__(self) -> str:
        return f'Type {self.name}() for interactive help, or {self.name}(object) for help about object.'

    def __call__(self, *args, **kwargs) -> None:
        if not (args or kwargs):
            print(
                "Welcome to the PyScript programming language! "
                "This is the help utility directly to the Python help.\n\n"
                "To get help on a specific object, type 'help(object)'.\n"
                "To get the list of builtin functions, types, exceptions, and other objects, type 'help(\"builtins\")'."
            )
        else:
            pyhelp(*args, **kwargs)

try:
    with (
        open(normpath(OTHER_PATH, 'copyright')) as copyright, 
        open(normpath(OTHER_PATH, 'credits')) as credits, 
        open(normpath(OTHER_PATH, 'license')) as license
    ):
        pys_sys.copyright = copyright.read()
        copyright = PysPrinter('copyright', pys_sys.copyright)
        credits = PysPrinter('credits', credits.read())
        license = PysPrinter('license', license.read())
except:
    pys_sys.copyright = ''
    copyright = PysPrinter('copyright', '')
    credits = PysPrinter('credits', '')
    license = PysPrinter('license', '')

help = PysHelper()

@PysBuiltinFunction
def require(pyfunc, name):

    """
    require(name: str | bytes) -> ModuleType | Any

    Import a PyScript module.

    name: A name or path of the module to be imported.
    """

    name, *other_components = normstr(name).split('>')
    code = pyfunc.__code__
    context = code.context
    filename = context.file.name
    path, module_path = find_module_path(filename, name)

    if module_path is None:
        if name == '_pyscript':
            from .. import core as module
        elif name == 'builtins':
            module = pys_builtins
        elif name == 'sys':
            module = pys_sys
        else:
            path = module_path = normpath(name)

    if module_path is not None:
        modules = pys_sys.modules
        module = modules.get(module_path, None)

        if module is None:
            loading_modules = pys_sys.loading_modules

            if os.path.isdir(module_path):
                raise ModuleNotFoundError(f"No module named {name!r}: Invalid module")

            elif module_path in loading_modules:
                raise ImportError(
                    f"cannot import module name {name!r} from partially initialized module {filename!r}, "
                    "mostly during circular import"
                )

            try:
                loading_modules.add(module_path)

                try:
                    with open(module_path, 'r', encoding='utf-8') as file:
                        file = PysFileBuffer(file, module_path)
                except FileNotFoundError as e:
                    raise ModuleNotFoundError(f"No module named {name!r}") from e
                except (IsADirectoryError, NotADirectoryError) as e:
                    raise ModuleNotFoundError(f"No module named {name!r}: Invalid module") from e
                except BaseException as e:
                    raise ImportError(f"Cannot import module named {name!r}: {e}") from e

                from .runner import pys_runner

                symtab, module = new_module_namespace(file=module_path, name=base(path))

                # minimize circular imports (python standard)
                modules[module_path] = module

                result = pys_runner(
                    file=file,
                    mode='exec',
                    symbol_table=symtab,
                    context_parent=context,
                    context_parent_entry_position=code.position
                )

                if result.error:
                    raise PysSignal(PysRunTimeResult().failure(result.error))

                # this can also get circular imports
                # modules[module_path] = module

            except:
                modules.pop(module_path, None)
                raise

            finally:
                loading_modules.discard(module_path)

    for component in other_components:
        module = getattr(module, component)

    return module

@PysBuiltinFunction
def pyimport(pyfunc, name):

    """
    pyimport(name: str | bytes) -> ModuleType

    Import a Python module.

    name: A name of the module to be imported.
    """

    dirpath = os.path.dirname(pyfunc.__code__.context.file.name)
    try:
        set_python_path(dirpath)
        return import_module(normstr(name))
    finally:
        remove_python_path(dirpath)

@PysBuiltinFunction
def breakpoint(pyfunc):

    """
    Pauses program execution and enters shell debugging mode.
    """

    if getattr(pys_sys, '__running_breakpoint__', False):
        raise RuntimeError("another breakpoint is still running")

    from .runner import pys_runner

    code = pyfunc.__code__
    context = code.context
    position = code.position
    symtab = context.symbol_table
    flags = context.flags
    colored = not (flags & NO_COLOR)
    colored_prompt = not (flags & NO_COLOR_PROMPT)
    scopes = []
    shell = (
        PysClassicLineShell
        if not ADVANCE_LINE_SHELL_SUPPORT or flags & CLASSIC_LINE_SHELL else
        PysPromptToolkitLineShell
    )(
        f'{GET_ACOLOR("bold-magenta")}(Pdb) {GET_ACOLOR("reset")}' if colored and colored_prompt else '(Pdb) ',
        f'{GET_ACOLOR("bold-magenta")}...   {GET_ACOLOR("reset")}' if colored and colored_prompt else '...   ',
        colored=colored
    )

    def show_line():
        print(f'> {context.file.name}({position.start_line}){context.name}')

    import_readline()
    show_line()

    try:
        pys_sys.__running_breakpoint__ = True

        while True:

            try:
                text = shell.prompt()
                if text == 1:
                    print("*** Unable to clean up namespace", file=sys.stderr)
                    continue

                split = ['exit'] if text == 0 else text.split()
                if split:
                    command, *args = split
                else:
                    command, args = '', ()

                if command in ('c', 'continue'):
                    return

                elif command in ('h', 'help'):
                    print(
                        "\n"
                        "Documented commands:\n"
                        "====================\n"
                        "(c)ontinue          : Exit the debugger and continue the program.\n"
                        "(d)own [count]      : Decrease the scope level (default one) to the older frame.\n"
                        "(h)elp              : Show this help display.\n"
                        "(l)ine              : Show the position where breakpoint() was called.\n"
                        "(q)uit / exit [code]: Exit the interpreter by throwing SystemExit.\n"
                        "(u)p [count]        : Increase the scope level (default one) to the older frame.\n"
                    )

                elif command in ('l', 'line'):
                    show_line()

                elif command in ('q', 'quit', 'exit'):
                    code = get_sequence(args, 0, '0')
                    raise SystemExit(int(code) if code.isdigit() else code)

                elif command in ('u', 'up'):
                    count = get_sequence(args, 0, '')
                    for _ in range(int(count) if count.isdigit() else 1):
                        if scopes:
                            symtab = scopes.pop()
                        else:
                            print('*** Oldest frame')
                            break

                elif command in ('d', 'down'):
                    count = get_sequence(args, 0, '')
                    parent = symtab.parent
                    for _ in range(int(count) if count.isdigit() else 1):
                        if parent is None:
                            print('*** Newest frame')
                            break
                        else:
                            scopes.append(symtab)
                            symtab = parent

                else:
                    exit_code, exit = pys_runner(
                        file=PysFileBuffer(text, '<breakpoint>'),
                        mode='single',
                        symbol_table=symtab
                    ).end_process()

                    if exit:
                        raise SystemExit(exit_code)

            except KeyboardInterrupt:
                shell.reset()
                print('\r--KeyboardInterrupt--', file=sys.stderr)

            except EOFError as e:
                raise SystemExit from e

    finally:
        pys_sys.__running_breakpoint__ = False

@PysBuiltinFunction
def globals(pyfunc):

    """
    Returns a dictionary containing the current global scope of variables.

    NOTE: Modifying the contents of a dictionary within a program or module scope will affect that scope. However,
    this does not apply to local scopes (creating a new dictionary).
    """

    original = pyfunc.__code__.context.symbol_table
    symbol_table = original.parent

    if symbol_table:
        result = {}

        while symbol_table:
            result |= symbol_table.symbols
            symbol_table = symbol_table.parent

        return result

    return original.symbols

@PysBuiltinFunction
def locals(pyfunc):

    """
    Returns a dictionary containing the current local scope of variables.

    NOTE: Changing the contents of the dictionary will affect the scope.
    """

    return pyfunc.__code__.context.symbol_table.symbols

@PysBuiltinFunction
def vars(pyfunc, *args):

    """
    Without arguments, equivalent to locals(). With an argument, equivalent to object.__dict__.
    """

    return pyvars(*args) if args else pyfunc.__code__.context.symbol_table.symbols

@PysBuiltinFunction
def dir(pyfunc, *args):

    """
    If called without an argument, return the names in the current scope. Else, return an alphabetized list of names
    comprising (some of) the attributes of the given object, and of attributes reachable from it. If the object supplies
    a method named __dir__, it will be used; otherwise the default dir() logic is used and returns:
        for a module object: the module's attributes.
        for a class object: its attributes, and recursively the attributes of its bases.
        for any other object: its attributes, its class's attributes, and recursively the attributes of its class's base
            classes.
    """

    return pydir(*args) if args else list(dkeys(pyfunc.__code__.context.symbol_table.symbols))

@PysBuiltinFunction
def exec(pyfunc, source, globals=None):

    """
    exec(source: str | bytes, globals: Optional[dict]) -> None

    Executes PyScript code statements from the given source.

    source: A string containing the code statements to be executed.
    globals: The namespace scope for the code that can be accessed, modified, and deleted. If not provided, the current
             local scope will be used.
    """

    if not isinstance(globals, optional_mapping):
        raise TypeError("exec(): globals must be dict")

    file = PysFileBuffer(source, '<exec>')
    code = pyfunc.__code__

    if globals is None:
        symtab = code.context.symbol_table
    else:
        symtab, _ = new_module_namespace(symbols=globals)

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=symtab,
        context_parent=code.context,
        context_parent_entry_position=code.position
    )

    if result.error:
        raise PysSignal(PysRunTimeResult().failure(result.error))

@PysBuiltinFunction
def eval(pyfunc, source, globals=None):

    """
    eval(source: str | bytes, globals: Optional[dict]) -> None

    Executes a PyScript code expression from the given source.

    source: A string containing the code statements to be executed.
    globals: The namespace scope for the code that can be accessed, modified, and deleted. If not provided, the current
             local scope will be used.
    """

    if not isinstance(globals, optional_mapping):
        raise TypeError("eval(): globals must be dict")

    file = PysFileBuffer(source, '<eval>')
    code = pyfunc.__code__

    if globals is None:
        symtab = code.context.symbol_table
    else:
        symtab, _ = new_module_namespace(symbols=globals)

    from .runner import pys_runner

    result = pys_runner(
        file=file,
        mode='eval',
        symbol_table=symtab,
        context_parent=code.context,
        context_parent_entry_position=code.position
    )

    if result.error:
        raise PysSignal(PysRunTimeResult().failure(result.error))

    return result.value

@PysBuiltinFunction
def ce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):

    """
    ce(a: Any, b: Any, *, rel_tol: Any = 1e-9, abs_tol: Any = 0) -> Any
    a ~= b

    Comparing two objects a and b to close equal.

    a, b: Two objects to be compared. If both are integer or float, it will call `math.isclose()` function. Otherwise,
          it will attempt to call the __ce__ method (if both fail, it calls the negated __nce__ method) of one of the
          two objects. If all else fails, it will throw a TypeError.
    rel_tol: maximum difference for being considered "close", relative to the magnitude of the input values.
    abs_tol: maximum difference for being considered "close", regardless of the magnitude of the input values.
    """

    if isinstance(a, real_number) and isinstance(b, real_number):
        return isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    success, result = _supported_method(pyfunc, a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = _supported_method(pyfunc, b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            success, result = _supported_method(pyfunc, a, '__nce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not success:
                success, result = _supported_method(pyfunc, b, '__nce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
                if not success:
                    raise TypeError(
                        f"unsupported operand type(s) for ~= or ce(): {type(a).__name__!r} and {type(b).__name__!r}"
                    )
            result = not result

    return result

@PysBuiltinFunction
def nce(pyfunc, a, b, *, rel_tol=1e-9, abs_tol=0):

    """
    nce(a: Any, b: Any, *, rel_tol: Any = 1e-9, abs_tol: Any = 0) -> Any
    a ~! b

    Comparing two objects a and b to not close equal.

    a, b: Two objects to be compared. If both are integer or float, it calls the `not math.isclose()` function.
          Otherwise, it attempts to call the __nce__ method (if both fail, it calls the negated __ce__ method) of one of
          the two objects. If both fail, it throws a TypeError.
    rel_tol: maximum difference for being considered "close", relative to the magnitude of the input values.
    abs_tol: maximum difference for being considered "close", regardless of the magnitude of the input values.
    """

    if isinstance(a, real_number) and isinstance(b, real_number):
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

@PysBuiltinFunction
def increment(pyfunc, object):

    """
    increment(object: Any) -> Any
    object++
    ++object

    Increase to the object. If the given type is integer or float, it will increment by 1, if the given type is unpack
    assignment (list, tuple, or set), it will increment each element. Otherwise, it will attempt to call the
    __increment__ method, which if unsuccessful will throw a TypeError.
    """

    if isinstance(object, real_number):
        return object + 1
    elif isinstance(object, sequence):
        return tuple(pyincrement(pyfunc, obj) for obj in object)

    success, result = _supported_method(pyfunc, object, '__increment__')
    if not success:
        raise TypeError(f"bad operand type for unary ++ or increment(): {type(object).__name__!r}")

    return result

@PysBuiltinFunction
def decrement(pyfunc, object):

    """
    decrement(object: Any) -> Any
    object--
    --object

    Decrease to the object. If the given type is integer or float, it will decrement by 1, if the given type is unpack
    assignment (list, tuple, or set), it will decrement each element. Otherwise, it will attempt to
    call the __decrement__ method, which if unsuccessful will throw a TypeError.
    """

    if isinstance(object, real_number):
        return object - 1
    elif isinstance(object, sequence):
        return tuple(pydecrement(pyfunc, obj) for obj in object)

    success, result = _supported_method(pyfunc, object, '__decrement__')
    if not success:
        raise TypeError(f"bad operand type for unary -- or decrement(): {type(object).__name__!r}")

    return result

@PysBuiltinFunction
def unpack(pyfunc, function, args=(), kwargs={}):

    """
    unpack(function: Callable, args: Iterable = (), kwargs: Mapping = {}) -> Any

    A replacement function for Python's argument unpack on function calls, which uses the syntax
    `function(*args, **kwargs)`.

    function: the function to be called.
    args: regular arguments (iterable object).
    kwargs: keyword arguments (mapping object).
    """

    code = pyfunc.__code__
    handle_call(function, code.context, code.position)
    return function(*args, **kwargs)

@PysBuiltinFunction
def comprehension(pyfunc, init, wrap, condition=None):

    """
    comprehension(
        init: Iterable[Any],
        wrap: Callable[[Any], Any],
        condition: Optional[Callable[[Any], bool]] = None
    ) -> Iterable[Any]

    A replacement function for Python's list comprehension, which uses the syntax
    `[wrap for item in init if condition]`.

    init: The iterable object to be iterated.
    wrap: The function that wraps the results of the iteration (Unpack per-iteration if parameter is more than 1).
    condition: The function that filters the iteration (Unpack per-iteration if parameter is more than 1).
    """

    if not callable(wrap):
        raise TypeError("comprehension(): wrap must be callable")
    if not (condition is None or callable(condition)):
        raise TypeError("comprehension(): condition must be callable")

    return map(
        _unpack_comprehension_function(pyfunc, wrap),
        init if condition is None else filter(_unpack_comprehension_function(pyfunc, condition), init)
    )

pyincrement = increment.__func__
pydecrement = decrement.__func__

pys_builtins = ModuleType(
    'builtins',
    "Built-in functions, types, exceptions, and other objects.\n\n"
    "This module provides direct access to all 'built-in' identifiers of PyScript and Python."
)

pys_builtins.__dict__.update({
    name: getattr(builtins, name)
    for name in pydir(builtins)
    if not (is_private_attribute(name) or is_blacklist_python_builtin(name))
})

pys_builtins.__dict__.update({
    'true': True,
    'false': False,
    'nil': None,
    'none': None,
    'null': None,
    'inf': inf,
    'infj': complex(0, inf),
    'nan': nan,
    'nanj': complex(0, nan),
    'copyright': copyright,
    'credits': credits,
    'license': license,
    'help': help,
    'require': require,
    'pyimport': pyimport,
    'breakpoint': breakpoint,
    'globals': globals,
    'locals': locals,
    'vars': vars,
    'dir': dir,
    'exec': exec,
    'eval': eval,
    'ce': ce,
    'nce': nce,
    'increment': increment,
    'decrement': decrement,
    'unpack': unpack,
    'comprehension': comprehension,
    'isobjectof': isobjectof
})