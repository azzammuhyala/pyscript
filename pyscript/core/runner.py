from .analyzer import PysAnalyzer
from .buffer import PysFileBuffer
from .cache import undefined, hook, PysUndefined
from .constants import PYSCRIPT_SHELL, PYSCRIPT_TYPECHECKING, DEFAULT, SILENT, RETRES, HIGHLIGHT, NO_COLOR
from .context import PysContext
from .exceptions import PysTraceback, PysSignal
from .handlers import handle_exception, handle_call, handle_execute
from .interpreter import visit
from .lexer import PysLexer
from .parser import PysParser
from .position import PysPosition
from .pysbuiltins import require
from .results import PysRunTimeResult, PysExecuteResult
from .symtab import PysSymbolTable, new_symbol_table
from .utils.ansi import BOLD, acolor
from .utils.debug import print_display
from .utils.decorators import typechecked
from .utils.generic import setimuattr, get_frame, get_locals
from .version import version

from os import environ
from sys import stderr, version as pyversion
from types import ModuleType
from typing import Any, Literal, Optional

def _normalize_globals(file, globals):
    if globals is None:
        symtab, _ = new_symbol_table(symbols=get_locals(3 if environ.get(PYSCRIPT_TYPECHECKING, '1') == '1' else 2))
    elif globals is undefined:
        symtab, _ = new_symbol_table(file=file.name, name='__main__')
    elif isinstance(globals, dict):
        symtab, _ = new_symbol_table(symbols=globals)
    return symtab

@typechecked
def pys_runner(
    file: PysFileBuffer,
    mode: Literal['exec', 'eval'],
    symbol_table: PysSymbolTable,
    flags: Optional[int] = None,
    context_parent: Optional[PysContext] = None,
    context_parent_entry_position: Optional[PysPosition] = None
) -> PysExecuteResult:

    context = PysContext(
        file=file,
        name='<program>',
        flags=flags,
        symbol_table=symbol_table,
        parent=context_parent,
        parent_entry_position=context_parent_entry_position
    )

    result = PysExecuteResult(context)
    runtime_runner_result = PysRunTimeResult()
    position = PysPosition(file, -1, -1)

    with handle_exception(runtime_runner_result, context, position):

        try:

            lexer = PysLexer(
                file=file,
                flags=context.flags & ~HIGHLIGHT,
                context_parent=context_parent,
                context_parent_entry_position=context_parent_entry_position
            )

            tokens, error = lexer.make_tokens()
            if error:
                return result.failure(error)

            parser = PysParser(
                tokens=tokens,
                flags=context.flags,
                context_parent=context_parent,
                context_parent_entry_position=context_parent_entry_position
            )

            ast = parser.parse(None if mode == 'exec' else parser.expr)
            if ast.error:
                return result.failure(ast.error)

            analyzer = PysAnalyzer(
                node=ast.node,
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

        setimuattr(context, 'flags', parser.flags)
        runtime_result = visit(ast.node, context)

        return (
            result.failure(runtime_result.error)
            if runtime_result.error else
            result.success(runtime_result.value)
        )

    if runtime_runner_result.error:
        return result.failure(runtime_runner_result.error)

@typechecked
def pys_exec(
    source,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> None | PysExecuteResult:

    """
    Execute a PyScript code from source given.

    Parameters
    ----------
    source: A valid PyScript source code.

    globals: A namespace dictionary or symbol table that can be accessed. \
             If it is None, it uses the current global namespace at the Python level. \
             If it is undefined, it creates a new default PyScript namespace.

    flags: A special flags.
    """

    file = PysFileBuffer(source)

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=_normalize_globals(file, globals),
        flags=flags
    )

    if flags & RETRES:
        return result

    elif result.error and not (flags & SILENT):
        raise PysSignal(PysRunTimeResult().failure(result.error))

@typechecked
def pys_eval(
    source,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> Any | PysExecuteResult:

    """
    Evaluate a PyScript code from source given.

    Parameters
    ----------
    source: A valid PyScript (Expression) source code.

    globals: A namespace dictionary or symbol table that can be accessed. \
             If it is None, it uses the current global namespace at the Python level. \
             If it is undefined, it creates a new default PyScript namespace.

    flags: A special flags.
    """

    file = PysFileBuffer(source)

    result = pys_runner(
        file=file,
        mode='eval',
        symbol_table=_normalize_globals(file, globals),
        flags=flags
    )

    if flags & RETRES:
        return result

    elif result.error and not (flags & SILENT):
        raise PysSignal(PysRunTimeResult().failure(result.error))

    return result.value

def pys_require(name) -> ModuleType | Any:

    """
    Import a PyScript module.

    Parameters
    ----------
    name: A name or path of the module to be imported.
    """

    file = PysFileBuffer('', get_frame(1).f_code.co_filename)
    handle_call(require, PysContext(file), PysPosition(file, -1, -1))
    return require(name)

@typechecked
def pys_shell(
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> int | Any:

    """
    Start an interactive PyScript shell.

    Parameters
    ----------
    globals: A namespace dictionary or symbol table that can be accessed. \
             If it is None, it uses the current global namespace at the Python level. \
             If it is undefined, it creates a new default PyScript namespace.

    flags: A special flags.
    """

    if environ.get(PYSCRIPT_SHELL, '0') == '1':
        raise RuntimeError("another shell is still running")

    file = PysFileBuffer('', '<pyscript-shell>')
    symtab = _normalize_globals(file, globals)

    if flags & NO_COLOR:
        reset = ''
        bmagenta = ''
    else:
        reset = acolor('reset')
        bmagenta = acolor('magenta', BOLD)

    line = 0
    parenthesis_level = 0
    in_string = False
    in_decorator = False
    is_triple_string = False
    next_line = False
    string_prefix = ''
    full_text = ''

    def reset_next_line():
        nonlocal parenthesis_level, in_string, in_decorator, string_prefix, is_triple_string, next_line, full_text
        parenthesis_level = 0
        in_string = False
        in_decorator = False
        string_prefix = ''
        is_triple_string = False
        next_line = False
        full_text = ''

    def is_next_line():
        return parenthesis_level > 0 or in_decorator or is_triple_string or next_line

    print(f'PyScript {version}')
    print(f'Python {pyversion}')
    print('Type "help" or "license" for more information; "exit" or "/exit" to exit the shell.')

    try:

        environ[PYSCRIPT_SHELL] = '1'
        hook.display = print_display

        while True:

            try:

                if is_next_line():
                    text = input(f'{bmagenta}{hook.ps2}{reset}')
                else:
                    text = input(f'{bmagenta}{hook.ps1}{reset}')
                    if text == '/exit':
                        return 0

                next_line = False
                in_decorator = False
                is_space = True
                i = 0

                while i < len(text):
                    character = text[i]

                    if character == '\\':
                        i += 1
                        character = text[i:i+1]

                        if character == '':
                            next_line = True
                            break

                    elif character in '\'"':
                        bind_3 = text[i:i+3]

                        if is_triple_string:
                            if len(bind_3) == 3 and string_prefix * 3 == bind_3:
                                in_string = False
                                is_triple_string = False
                                i += 2

                        else:
                            if not in_string and bind_3 in ("'''", '"""'):
                                is_triple_string = True
                                i += 2

                            if in_string and string_prefix == character:
                                in_string = False
                            else:
                                string_prefix = character
                                in_string = True

                    if not in_string:

                        if character == '#':
                            break

                        elif is_space and character == '@':
                            in_decorator = True
                            i += 1
                            continue

                        elif character in '([{':
                            parenthesis_level += 1

                        elif character in ')]}':
                            parenthesis_level -= 1

                        if not character.isspace():
                            is_space = False

                    i += 1

                if in_decorator and is_space:
                    in_decorator = False

                if in_string and not (next_line or is_triple_string):
                    in_string = False
                    parenthesis_level = 0

                if is_next_line():
                    full_text += text + '\n'
                    continue

                result = pys_runner(
                    file=PysFileBuffer(full_text + text, f'<pyscript-shell-{line}>'),
                    mode='exec',
                    symbol_table=symtab,
                    flags=flags
                )

                if result.error:
                    if result.error.exception is SystemExit:
                        return 0
                    if type(result.error.exception) is SystemExit:
                        return result.error.exception.code

                flags = result.context.flags
                code = handle_execute(result)
                if code == 0:
                    line += 1

                reset_next_line()

            except KeyboardInterrupt:
                reset_next_line()
                print(f'\r{bmagenta}KeyboardInterrupt{reset}', file=stderr)

            except EOFError:
                print()
                return 0

    finally:
        environ[PYSCRIPT_SHELL] = '0'
        hook.display = None