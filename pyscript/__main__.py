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
from .core.runner import _namespace_to_symbol_table, pys_runner, pys_shell
from .core.utils.debug import USE_NOTEBOOK
from .core.utils.generic import is_environ
from .core.utils.module import find_module_path, remove_python_path
from .core.utils.path import getcwd, base, normpath
from .core.version import __version__

if PYGMENTS:
    from pygments import highlight
    from pygments.formatters import (
        BBCodeFormatter, HtmlFormatter, LatexFormatter, TerminalFormatter, TerminalTrueColorFormatter,
        Terminal256Formatter
    )

    FORMATER_PYGMENTS_MAP = {
        'pm-bbcode': BBCodeFormatter,
        'pm-html': HtmlFormatter,
        'pm-latex': LatexFormatter,
        'pm-terminal': TerminalFormatter,
        'pm-true-terminal': TerminalTrueColorFormatter,
        'pm-256-terminal': Terminal256Formatter
    }

from argparse import OPTIONAL, REMAINDER, ArgumentParser

import sys

FORMATER_HIGHLIGHT_MAP = {
    'html': HLFMT_HTML,
    'ansi': HLFMT_ANSI,
    'bbcode': HLFMT_BBCODE
}

EDITOR_MAP = {}
for supported, name, class_editor in [
    (GUI_SUPPORT,      'gui',      PysGUIEditor),
    (TERMINAL_SUPPORT, 'terminal', PysTerminalEditor)
]:
    if supported:
        EDITOR_MAP[name] = class_editor

arguments_requiring_value = {'-l', '--highlight', '-r', '--py-recursion'}

parser = ArgumentParser(
    prog=f'{base(sys.executable)} -m pyscript',
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
    metavar='STRING',
    help="execute program from a string argument",
)

parser.add_argument(
    '-d', '-O', '--debug',
    action='store_true',
    help="set a debug flag, this will ignore assert statement. Check the flag is active with the __debug__ keyword"
)

if EDITOR_MAP:
    parser.add_argument(
        '-e', '--editor',
        choices=tuple(EDITOR_MAP.keys()),
        default=None,
        help="open the editor panel from a 'file'",
    )
    arguments_requiring_value.update({'-e', '--editor'})

parser.add_argument(
    '-i', '--inspect',
    action='store_true',
    help="inspect interactively after running a code",
)

parser.add_argument(
    '-k', '--classic-line-shell',
    action='store_true',
    help="use a classic command line shell"
)

parser.add_argument(
    '-l', '--highlight',
    choices=tuple(FORMATER_HIGHLIGHT_MAP.keys()) + tuple(FORMATER_PYGMENTS_MAP.keys() if PYGMENTS else ()),
    default=None,
    help="generate highlight code from a 'file'"
)

parser.add_argument(
    '-m', '--module',
    type=str,
    default=None,
    metavar='NAME',
    help="run library module as a script"
)

parser.add_argument(
    '-n', '--no-color',
    action='store_true',
    help="suppress colored output"
)

parser.add_argument(
    '-p', '--no-color-prompt',
    action='store_true',
    help="suppress colored prompt output"
)

parser.add_argument(
    '-r', '--py-recursion',
    type=int,
    default=None,
    metavar='UINTEGER',
    help="set a Python recursion limit"
)

parser.add_argument(
    '-t', '--terminal',
    action='store_true',
    help="configure terminal encoding to UTF-8 and enable ANSI escape code processing on Windows"
)

parser.add_argument(
    '-q',
    action='store_true',
    help="don't print version and copyright messages on interactive startup"
)

parser.add_argument(
    '-v', '-V', '--version',
    action='version',
    version=f"PyScript {__version__}",
)

parser.add_argument(
    '-P',
    action='store_true',
    help="don't prepend a potentially unsafe path to sys.path (python sys.path)"
)

parser.add_argument(
    'file',
    type=str,
    nargs=OPTIONAL,
    default=None,
    help="file path to be executed"
)

parser.add_argument(
    'arg',
    nargs=REMAINDER,
    help="remaining arguments stored in pys_sys.argv (pyscript sys.argv)"
)

def argument_error(argument, message):
    parser.print_usage(sys.stderr)
    parser.exit(2, f"{parser.prog}: error: argument {argument}: {message}\n")

argv = sys.argv[1:]
argc = len(argv)
index = 0
arg_index = -1

while index < argc:
    arg = argv[index]
    if not arg.startswith('-') or arg == '--':
        break

    if arg in ('-c', '--command'):
        arg_index = index + 2
        break
    elif arg in ('-m', '--module'):
        arg_index = index + 2
        break

    index += 1
    if arg in arguments_requiring_value:
        index += 1

args = parser.parse_args(argv if arg_index == -1 else argv[:arg_index])
arg  = args.arg               if arg_index == -1 else argv[arg_index:]

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
    (args.notebook           or USE_NOTEBOOK,                                NOTEBOOK),
    (args.classic_line_shell or is_environ(ENV_PYSCRIPT_CLASSIC_LINE_SHELL), CLASSIC_LINE_SHELL),
    (args.no_color           or is_environ('NO_COLOR'),                      NO_COLOR),
    (args.no_color_prompt    or is_environ(ENV_PYSCRIPT_NO_COLOR_PROMPT),    NO_COLOR_PROMPT),
    (args.debug,                                                             DEBUG),
    (args.q,                                                                 DONT_SHOW_BANNER_ON_SHELL)
]:
    if condition:
        flags |= flag

if args.P:
    for cwd in {'', '.', getcwd()}:
        remove_python_path(cwd)

pys_sys.argv = argv = ['', *arg]

def clean_up() -> None:
    g = globals()

    for name in {
        'ArgumentParser', 'BBCodeFormatter', 'CLASSIC_LINE_SHELL', 'DEBUG', 'DEFAULT', 'DONT_SHOW_BANNER_ON_SHELL',
        'EDITOR_MAP', 'ENV_PYSCRIPT_CLASSIC_LINE_SHELL', 'ENV_PYSCRIPT_NO_COLOR_PROMPT', 'FORMATER_HIGHLIGHT_MAP',
        'FORMATER_PYGMENTS_MAP', 'GUI_SUPPORT', 'HLFMT_ANSI', 'HLFMT_BBCODE', 'HLFMT_HTML', 'HtmlFormatter',
        'LatexFormatter', 'NOTEBOOK', 'NO_COLOR', 'NO_COLOR_PROMPT', 'OPTIONAL', 'PYGMENTS', 'PygmentsPyScriptLexer',
        'PygmentsPyScriptStyle', 'PysFileBuffer', 'PysGUIEditor', 'PysTerminalEditor', 'REMAINDER', 'TERMINAL_SUPPORT',
        'Terminal256Formatter', 'TerminalFormatter', 'TerminalTrueColorFormatter', 'USE_NOTEBOOK', '__version__',
        '_namespace_to_symbol_table', 'arg', 'arg_index', 'argc', 'args', 'argument_error', 'arguments_requiring_value',
        'argv', 'base', 'class_editor', 'clean_up', 'condition', 'ctypes', 'execute', 'fd', 'file', 'find_module_path',
        'flag', 'getcwd', 'highlight', 'i', 'index', 'is_environ', 'kernel32', 'load_file', 'module_path', 'name',
        'normpath', 'parser', 'pys_highlight', 'pys_sys', 'remove_python_path', 'supported'
    }:
        try:
            del g[name]
        except:
            continue

def load_file(path) -> PysFileBuffer:
    file = PysFileBuffer('', path)
    try:
        with open(path, 'r', encoding='utf-8') as file:
            file = PysFileBuffer(file, path)
    except FileNotFoundError:
        if not (EDITOR_MAP and args.editor):
            argument_error('file', f"can't open file \"{path}\": No such file or directory")
    except PermissionError:
        argument_error('file', f"can't open file \"{path}\": Permission denied")
    except IsADirectoryError:
        argument_error('file', f"can't open file \"{path}\": Path is not a file")
    except NotADirectoryError:
        argument_error('file', f"can't open file \"{path}\": Attempting to access directory from file")
    except (OSError, IOError):
        argument_error('file', f"can't open file \"{path}\": Attempting to access a system directory or file")
    except UnicodeDecodeError:
        argument_error('file', f"can't read file \"{path}\": Bad file")
    except BaseException as e:
        argument_error('file', f"file \"{path}\": Unexpected error: {e}")
    return file

def execute(file: PysFileBuffer) -> None:
    global code

    not_show_banner_flag = DONT_SHOW_BANNER_ON_SHELL
    inspect = args.inspect
    symtab = _namespace_to_symbol_table(undefined, file)

    clean_up()

    result = pys_runner(
        file=file,
        mode='exec',
        symbol_table=symtab,
        flags=flags
    )

    code, _ = result.end_process()

    if inspect:
        if sys.stdout.closed or sys.stderr.closed:
            code = 1
        elif sys.stdin.closed:
            print("Can't run interactive shell: sys.stdin closed", file=sys.stderr)
            code = 1
        else:
            code = pys_shell(
                globals=result.context.symbol_table,
                flags=result.context.flags | not_show_banner_flag,
                parser_flags=result.parser_flags
            )

if args.file is not None:
    argv[0] = args.file
    file = load_file(normpath(args.file))

    if EDITOR_MAP and args.editor:
        try:
            EDITOR_MAP[args.editor](file=file, colored=not (flags & NO_COLOR)).run()
        except BaseException as e:
            argument_error('-e/--editor', e)

    elif args.highlight:
        try:
            if args.highlight in FORMATER_HIGHLIGHT_MAP:
                print(
                    pys_highlight(
                        source=file,
                        formatter=FORMATER_HIGHLIGHT_MAP[args.highlight]
                    )
                )
            else:
                print(
                    highlight(
                        code=file.text,
                        lexer=PygmentsPyScriptLexer(),
                        formatter=FORMATER_PYGMENTS_MAP[args.highlight](style=PygmentsPyScriptStyle, full=True)
                    )
                )
        except BaseException as e:
            argument_error('-l/--highlight', e)

    else:
        execute(file)

elif args.module is not None:
    _, module_path = find_module_path(None, args.module, '__main__')
    if module_path is None:
        argument_error('-m/--module', f"can't find module \"{args.module}\"")

    file = load_file(module_path)
    argv[0] = file.name
    execute(file)

elif args.command is not None:
    argv[0] = '-c'
    execute(PysFileBuffer(args.command, '<arg-command>'))

else:
    clean_up()
    code = pys_shell(
        globals=undefined,
        flags=flags
    )

# goodbye ;)
sys.exit(code)