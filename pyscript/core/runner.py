from .analyzer import PysAnalyzer
from .buffer import PysFileBuffer
from .cache import pys_sys, undefined, PysUndefined
from .constants import (
    LIBRARIES_PATH, OTHER_PATH, SITE_PACKAGES_PATH, DEFAULT, SILENT, RETURN_RESULT, NO_COLOR, DONT_SHOW_BANNER_ON_SHELL,
    CLASSIC_LINE_SHELL, NO_COLOR_PROMPT
)
from .context import PysContext
from .exceptions import PysTraceback, PysSignal
from .handlers import handle_call
from .interpreter import get_visitor
from .lexer import PysLexer
from .mapping import GET_ACOLORS
from .parser import PysParser
from .position import PysPosition
from .pysbuiltins import require
from .results import PysRunTimeResult, PysExecuteResult
from .shell import PysClassicLineShell, PysPromptToolkitLineShell, ADVANCE_LINE_SHELL_SUPPORT
from .symtab import PysSymbolTable, new_module_namespace
from .utils.debug import import_readline
from .utils.decorators import TYPECHECK_STACK, typechecked
from .utils.generic import get_frame, get_locals
from .version import version

from types import ModuleType
from typing import Any, Literal, Optional

import os
import sys

def _normalize_namespace(namespace: PysUndefined | PysSymbolTable | dict | None, file: PysFileBuffer) -> PysSymbolTable:
    if namespace is None:
        symtab, _ = new_module_namespace(symbols=get_locals(2 + TYPECHECK_STACK))
    elif namespace is undefined:
        symtab, _ = new_module_namespace(file=file.name, name='__main__')
    elif isinstance(namespace, dict):
        symtab, _ = new_module_namespace(symbols=namespace)
    else:
        symtab = namespace
    return symtab

@typechecked
def pys_runner(
    file: PysFileBuffer,
    mode: Literal['exec', 'eval', 'single'],
    symbol_table: PysSymbolTable,
    flags: Optional[int] = None,
    parser_flags: int = DEFAULT,
    context_parent: Optional[PysContext] = None,
    context_parent_entry_position: Optional[PysPosition] = None
) -> PysExecuteResult:

    """
    The core of execution PyScript code.

    Parameters
    ----------
    - file : Buffer object from PysFileBuffer (`pyscript.core.buffer.PysFileBuffer`).

    - mode : Complication and execution mode. 'exec' to compile a whole code block, 'eval' to compile a single
             expression. 'single' is typically used for interactive shells (prints the result value, compile within a
             whole code block or expression).

    - symbol_table : Symbol table scope (`pyscript.core.symtab.PysSymbolTable`).

    - flags : A special flag (If None then it automatically uses flags from context_parent, and if not available then
              flags are set to DEFAULT).

    - parser_flags : A special parser flag.

    - context_parent : The parent context object, useful for linking tracebacks (context_parent_entry_position is
                       required).

    - context_parent_entry_position : The last parent position object, useful for specifying the row and column
                                      sections in the traceback (context_parent is required).

    Returns
    -------
    A PysExecuteResult object (`pyscript.core.results.PysExecuteResult`), which contains the execution result value,
    error, and the context after execution.
    """

    if (context_parent is None) != (context_parent_entry_position is None):
        raise TypeError("context_parent and context_parent_entry_position both must be filled in")

    context = PysContext(
        file=file,
        name='<program>',
        flags=flags,
        symbol_table=symbol_table,
        parent=context_parent,
        parent_entry_position=context_parent_entry_position
    )

    result = PysExecuteResult(context, parser_flags)
    runtime_result = PysRunTimeResult()
    position = PysPosition(file, -1, -1)

    with runtime_result(context, position):

        try:

            lexer = PysLexer(
                file=file,
                flags=context.flags,
                context_parent=context_parent,
                context_parent_entry_position=context_parent_entry_position
            )

            tokens, error = lexer.make_tokens()
            if error:
                return result.failure(error)

            parser = PysParser(
                tokens=tokens,
                flags=context.flags,
                parser_flags=parser_flags,
                context_parent=context_parent,
                context_parent_entry_position=context_parent_entry_position
            )

            node, error = parser.parse(parser.expression if mode == 'eval' else None)
            if error:
                return result.failure(error)

            analyzer = PysAnalyzer(
                node=node,
                flags=parser.flags,
                context_parent=context_parent,
                context_parent_entry_position=context_parent_entry_position
            )

            error = analyzer.analyze()
            if error:
                return result.failure(error)

        except RecursionError:
            return result.failure(
                PysTraceback(
                    RecursionError("maximum recursion depth exceeded during complication"),
                    context,
                    position
                )
            )

        result.parser_flags = parser.parser_flags
        pys_sys.flags = context.flags

        visitor_result = get_visitor(node.__class__)(node, context)

        if visitor_result.error:
            return result.failure(visitor_result.error)

        if mode == 'single' and (displayhook := pys_sys.displayhook) is not None:
            handle_call(displayhook, context, position)
            displayhook(visitor_result.value)

        return result.success(visitor_result.value)

    return result.failure(runtime_result.error) if runtime_result.error else result

@typechecked
def pys_exec(
    source,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT,
    parser_flags: int = DEFAULT
) -> None | PysExecuteResult:

    """
    Execute a PyScript code from source given.

    Parameters
    ----------
    - source : A valid PyScript source code.

    - globals : A namespace dictionary or symbol table that can be accessed.
                If it is None, it uses the current global namespace at the Python level.
                If it is undefined, it creates a new default PyScript namespace.

    - flags : A special flags.

    - parser_flags : A special parser flags.

    Returns
    -------
    If `flags` has `RETURN_RESULT`, it returns a PysExecuteResult object (`pyscript.core.results.PysExecuteResult`),
    which contains the execution result value, error, and the context after execution. Otherwise, it returns None.
    """

    file = PysFileBuffer(source)

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=_normalize_namespace(globals, file),
        flags=flags,
        parser_flags=parser_flags
    )

    if flags & RETURN_RESULT:
        return result

    elif result.error and not (flags & SILENT):
        raise PysSignal(PysRunTimeResult().failure(result.error))

@typechecked
def pys_eval(
    source,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT,
    parser_flags: int = DEFAULT
) -> Any | PysExecuteResult:

    """
    Evaluate a PyScript code from source given.

    Parameters
    ----------
    - source : A valid PyScript (Expression) source code.

    - globals : A namespace dictionary or symbol table that can be accessed.
                If it is None, it uses the current global namespace at the Python level.
                If it is undefined, it creates a new default PyScript namespace.

    - flags : A special flags.

    - parser_flags : A special parser flags.

    Returns
    -------
    If `flags` has `RETURN_RESULT`, it returns a PysExecuteResult object (`pyscript.core.results.PysExecuteResult`),
    which contains the execution result value, error, and the context after execution. Otherwise, it returns the
    execution result value directly.
    """

    file = PysFileBuffer(source)

    result = pys_runner(
        file=file,
        mode='eval',
        symbol_table=_normalize_namespace(globals, file),
        flags=flags,
        parser_flags=parser_flags
    )

    if flags & RETURN_RESULT:
        return result

    elif result.error and not (flags & SILENT):
        raise PysSignal(PysRunTimeResult().failure(result.error))

    return result.value

@typechecked
def pys_require(name, flags: int = DEFAULT) -> ModuleType | Any:

    """
    Import a PyScript module.

    Parameters
    ----------
    - name : A name or path of the module to be imported.

    - flags : A special flags.

    Returns
    -------
    A module object or other any object (using `>`).
    """

    file = PysFileBuffer('', get_frame(1 + TYPECHECK_STACK).f_code.co_filename)
    handle_call(require, PysContext(file=file, flags=flags), PysPosition(file, -1, -1))
    return require(name)

@typechecked
def pys_shell(
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT,
    parser_flags: int = DEFAULT
) -> int | Any:

    """
    Start an interactive PyScript shell.

    Parameters
    ----------
    - globals : A namespace dictionary or symbol table that can be accessed.
                If it is None, it uses the current global namespace at the Python level.
                If it is undefined, it creates a new default PyScript namespace.

    - flags : A special flags.

    - parser_flags : A special parser flags.

    Returns
    -------
    Shell exit code. Sometimes the exit code is an other object.
    """

    if pys_sys.__running_shell__:
        raise RuntimeError("another shell is still running")

    line = 0
    default_parser_flags = parser_flags
    file = PysFileBuffer('', '<pyscript-shell>')
    symtab = _normalize_namespace(globals, file)
    colored = not (flags & NO_COLOR)
    colored_prompt = not (flags & NO_COLOR_PROMPT)
    shell = (
        PysClassicLineShell
        if not ADVANCE_LINE_SHELL_SUPPORT or flags & CLASSIC_LINE_SHELL else
        PysPromptToolkitLineShell
    )(colored=colored)

    if colored:
        reset = GET_ACOLORS('reset')
        bmagenta = GET_ACOLORS('bold-magenta')
    else:
        reset = ''
        bmagenta = ''

    import_readline()

    if not (flags & DONT_SHOW_BANNER_ON_SHELL):

        for path in (LIBRARIES_PATH, OTHER_PATH, SITE_PACKAGES_PATH):
            if not os.path.isdir(path):
                print(f'WARNING: "{path}" directory not found', file=sys.stderr)

        print(
            f'PyScript {version}\n'
            f'Python {sys.version}\n'
            'Type "help", "copyright", "credits" or "license" for more information.\n'
            'Type "quit", "exit" or "/exit" to exit the shell; "/clear" to clear the shell; "/clean" to clean up the '
            'namespace.'
        )

    try:
        pys_sys.__running_shell__ = True

        while True:

            try:
                shell.ps1 = f'{bmagenta}{pys_sys.ps1}{reset}' if colored and colored_prompt else pys_sys.ps1
                shell.ps2 = f'{bmagenta}{pys_sys.ps2}{reset}' if colored and colored_prompt else pys_sys.ps2

                text = shell.prompt()
                if text == 0:
                    return 0
                elif text == 1:
                    symtab = _normalize_namespace(undefined, file)
                    parser_flags = default_parser_flags
                    line = 0
                    continue

                result = pys_runner(
                    file=PysFileBuffer(text, f'<pyscript-shell-{line}>'),
                    mode='single',
                    symbol_table=symtab,
                    flags=flags,
                    parser_flags=parser_flags
                )

                parser_flags = result.parser_flags
                code, exit = result.end_process()
                if exit:
                    return code
                elif code == 0:
                    line += 1

            except KeyboardInterrupt:
                shell.reset()
                print(f'\r{bmagenta}KeyboardInterrupt{reset}', file=sys.stderr)

            except EOFError:
                print()
                return 0

    finally:
        pys_sys.__running_shell__ = False