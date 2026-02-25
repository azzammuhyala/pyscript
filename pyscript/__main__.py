from .core.buffer import PysFileBuffer
from .core.cache import pys_sys, undefined
from .core.constants import (
    ENV_PYSCRIPT_NO_COLOR_PROMPT, ENV_PYSCRIPT_CLASSIC_LINE_SHELL, DEFAULT, DEBUG, NO_COLOR, DONT_SHOW_BANNER_ON_SHELL,
    CLASSIC_LINE_SHELL, NO_COLOR_PROMPT, NOTEBOOK
)
from .core.editor.gui import PysGUIEditor, GUI_SUPPORT
from .core.editor.terminal import PysTerminalEditor, TERMINAL_SUPPORT
from .core.highlight import (
    PYGMENTS, HLFMT_HTML, HLFMT_ANSI, HLFMT_BBCODE, pys_highlight, PygmentsPyScriptStyle, PygmentsPyScriptLexer
)
from .core.runner import _normalize_namespace, pys_runner, pys_shell
from .core.utils.debug import USE_NOTEBOOK
from .core.utils.generic import is_environ
from .core.utils.module import remove_python_path
from .core.utils.path import getcwd, normpath, get_name_from_path
from .core.version import __version__

if PYGMENTS:
    from pygments import highlight
    from pygments.formatters import (
        BBCodeFormatter, HtmlFormatter, LatexFormatter, TerminalFormatter, TerminalTrueColorFormatter,
        Terminal256Formatter
    )

    FORMAT_PYGMENTS_MAP = {
        'pm-bbcode': BBCodeFormatter,
        'pm-html': HtmlFormatter,
        'pm-latex': LatexFormatter,
        'pm-terminal': TerminalFormatter,
        'pm-true-terminal': TerminalTrueColorFormatter,
        'pm-256-terminal': Terminal256Formatter
    }

from argparse import OPTIONAL, REMAINDER, ArgumentParser

import sys

FORMAT_HIGHLIGHT_MAP = {
    'html': HLFMT_HTML,
    'ansi': HLFMT_ANSI,
    'bbcode': HLFMT_BBCODE
}

EDITOR_MAP = {}

for supported, name, class_editor in [
    (GUI_SUPPORT, 'gui', PysGUIEditor),
    (TERMINAL_SUPPORT, 'terminal', PysTerminalEditor)
]:
    if supported:
        EDITOR_MAP[name] = class_editor

parser = ArgumentParser(
    prog=f'{get_name_from_path(sys.executable)} -m pyscript',
    description=f'PyScript Launcher for Python Version {".".join(map(str, sys.version_info))}'
)

parser.add_argument(
    '-b', '--notebook',
    action='store_true',
    help="combination of -k and -p flags, suitable for notebook platforms such as IPython, Jupyter, Google Colab, etc"
)

parser.add_argument(
    '-c', '--command',
    type=str,
    default=None,
    help="Execute program from a string argument",
)

parser.add_argument(
    '-d', '-O', '--debug',
    action='store_true',
    help="Set a debug flag, this will ignore assert statement. Check the flag is active with the __debug__ keyword"
)

if EDITOR_MAP:
    parser.add_argument(
        '-e', '--editor',
        choices=tuple(EDITOR_MAP.keys()),
        default=None,
        help="Open the editor panel from a 'file'",
    )

parser.add_argument(
    '-i', '--inspect',
    action='store_true',
    help="Inspect interactively after running a code",
)

parser.add_argument(
    '-k', '--classic-line-shell',
    action='store_true',
    help="Use a classic command line shell"
)

parser.add_argument(
    '-l', '--highlight',
    choices=tuple(FORMAT_HIGHLIGHT_MAP.keys()) + tuple(FORMAT_PYGMENTS_MAP.keys() if PYGMENTS else ()),
    default=None,
    help="Generate highlight code from a 'file'"
)

parser.add_argument(
    '-n', '--no-color',
    action='store_true',
    help="Suppress colored output"
)

parser.add_argument(
    '-p', '--no-color-prompt',
    action='store_true',
    help="Suppress colored prompt output"
)

parser.add_argument(
    '-r', '--py-recursion',
    type=int,
    default=None,
    help="Set a Python recursion limit"
)

parser.add_argument(
    '-t', '--terminal',
    action='store_true',
    help="Configure terminal encoding to UTF-8 and enable ANSI escape code processing on Windows"
)

parser.add_argument(
    '-q',
    action='store_true',
    help="Don't print version and copyright messages on interactive startup"
)

parser.add_argument(
    '-v', '-V', '--version',
    action='version',
    version=f"PyScript {__version__}",
)

parser.add_argument(
    '-P',
    action='store_true',
    help="Don't prepend a potentially unsafe path to sys.path (python sys.path)"
)

parser.add_argument(
    'file',
    type=str,
    nargs=OPTIONAL,
    default=None,
    help="File path to be executed"
)

parser.add_argument(
    'arg',
    nargs=REMAINDER,
    help="Remaining arguments stored in pys_sys.argv (sys.argv)"
)

def argument_error(argument, message):
    parser.print_usage(sys.stderr)
    parser.exit(2, f"{parser.prog}: error: argument {argument}: {message}\n")

args = parser.parse_args()

if args.terminal:

    for fd in (sys.stdout, sys.stderr, sys.stdin):
        try:
            fd.reconfigure(encoding='utf-8')
        except:
            continue

    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            for i in (-11, -12, -10):
                try:
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(i), 7)
                except:
                    continue
        except:
            pass

if args.file is None:
    if EDITOR_MAP and args.editor:
        argument_error('-e/--editor', "argument 'file' is required")
    elif args.highlight:
        argument_error('-l/--highlight', "argument 'file' is required")

if args.py_recursion is not None:
    try:
        sys.setrecursionlimit(args.py_recursion)
    except BaseException as e:
        argument_error('-r/--py-recursion', e)

code = 0
flags = DEFAULT

for condition, flag in [
    (args.notebook or USE_NOTEBOOK, NOTEBOOK),
    (args.debug, DEBUG),
    (args.classic_line_shell or is_environ(ENV_PYSCRIPT_CLASSIC_LINE_SHELL), CLASSIC_LINE_SHELL),
    (args.no_color or is_environ('NO_COLOR'), NO_COLOR),
    (args.no_color_prompt or is_environ(ENV_PYSCRIPT_NO_COLOR_PROMPT), NO_COLOR_PROMPT),
    (args.q, DONT_SHOW_BANNER_ON_SHELL)
]:
    if condition:
        flags |= flag

if args.P:
    for cwd in {'', '.', getcwd()}:
        remove_python_path(cwd)

pys_sys.argv = argv = ['', *args.arg]

if args.file is not None:
    argv[0] = args.file
    path = normpath(args.file)

    try:
        with open(path, 'r', encoding='utf-8') as file:
            file = PysFileBuffer(file, path)
    except FileNotFoundError:
        if EDITOR_MAP and args.editor:
            file = PysFileBuffer('', path)
        else:
            parser.error(f"can't open file {path!r}: No such file or directory")
    except PermissionError:
        parser.error(f"can't open file {path!r}: Permission denied")
    except IsADirectoryError:
        parser.error(f"can't open file {path!r}: Path is not a file")
    except NotADirectoryError:
        parser.error(f"can't open file {path!r}: Attempting to access directory from file")
    except (OSError, IOError):
        parser.error(f"can't open file {path!r}: Attempting to access a system directory or file")
    except UnicodeDecodeError:
        parser.error(f"can't read file {path!r}: Bad file")
    except BaseException as e:
        parser.error(f"file {path!r}: Unexpected error: {e}")

    if EDITOR_MAP and args.editor:
        try:
            EDITOR_MAP[args.editor](file).run()
        except BaseException as e:
            argument_error('-e/--editor', e)

    elif args.highlight:
        try:
            if args.highlight in FORMAT_HIGHLIGHT_MAP:
                print(
                    pys_highlight(
                        source=file,
                        formatter=FORMAT_HIGHLIGHT_MAP[args.highlight]
                    )
                )
            else:
                print(
                    highlight(
                        code=file.text,
                        lexer=PygmentsPyScriptLexer(),
                        formatter=FORMAT_PYGMENTS_MAP[args.highlight](style=PygmentsPyScriptStyle, full=True)
                    )
                )
        except BaseException as e:
            argument_error('-l/--highlight', e)

    else:
        result = pys_runner(
            file=file,
            mode='exec',
            symbol_table=_normalize_namespace(file, undefined),
            flags=flags
        )

        code, _ = result.end_process()

        if args.inspect and not (sys.stdout.closed or sys.stderr.closed):
            if sys.stdin.closed:
                print("Can't run interactive shell: sys.stdin closed", file=sys.stderr)
                code = 1
            else:
                code = pys_shell(
                    globals=result.context.symbol_table,
                    flags=result.context.flags | DONT_SHOW_BANNER_ON_SHELL,
                    parser_flags=result.parser_flags
                )

elif args.command is not None:
    argv[0] = '-c'

    file = PysFileBuffer(args.command, '<arg-command>')
    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=_normalize_namespace(file, undefined),
        flags=flags
    )

    code, _ = result.end_process()

    if args.inspect and not (sys.stdout.closed or sys.stderr.closed):
        if sys.stdin.closed:
            print("Can't run interactive shell: sys.stdin closed", file=sys.stderr)
            code = 1
        else:
            code = pys_shell(
                globals=result.context.symbol_table,
                flags=result.context.flags | DONT_SHOW_BANNER_ON_SHELL,
                parser_flags=result.parser_flags
            )

else:
    code = pys_shell(
        globals=undefined,
        flags=flags
    )

sys.exit(code)