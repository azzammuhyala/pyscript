from .core.buffer import PysFileBuffer
from .core.cache import undefined
from .core.constants import DEFAULT, DEBUG, NO_COLOR
from .core.handlers import handle_execute
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, pys_highlight
from .core.runner import pys_runner, pys_shell
from .core.symtab import build_symbol_table
from .core.utils.general import normalize_path
from .core.version import __version__

from argparse import ArgumentParser

from sys import executable, version_info, exit, setrecursionlimit
from os.path import basename, splitext

parser = ArgumentParser(
    prog=splitext(basename(executable))[0] + ' -m pyscript',
    description='PyScript Launcher for Python Version ' + '.'.join(map(str, version_info))
)

parser.add_argument(
    'file',
    type=str,
    nargs='?',
    default=None,
    help="file path"
)

parser.add_argument(
    '-v', '--version',
    action='version',
    version=f"PyScript {__version__}",
)

parser.add_argument(
    '-c', '--command',
    type=str,
    default=None,
    help="execute PyScript from argument",
)

parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help="set a debug flag, this will remove the assert statement"
)

parser.add_argument(
    '-i', '--inspect',
    action='store_true',
    help="inspect interactively after running a file",
)

parser.add_argument(
    '-l', '--highlight',
    choices=('html', 'ansi'),
    default=None,
    help='generate PyScript highlight code from a file'
)

parser.add_argument(
    '-n', '--no-color',
    action='store_true',
    help="no colorful traceback"
)

parser.add_argument(
    '-r', '--py-recursion',
    type=int,
    default=None,
    help="set a python recursion limit"
)

args = parser.parse_args()

if args.highlight and args.file is None:
    parser.error("-l, --highlight: file path require")

if args.py_recursion is not None:
    try:
        setrecursionlimit(args.py_recursion)
    except BaseException as e:
        parser.error(f"-r, --py-recursion: {e}")

code = 0
flags = DEFAULT

if args.debug:
    flags |= DEBUG
if args.no_color:
    flags |= NO_COLOR

if args.file is not None:
    path = normalize_path(args.file)

    try:
        with open(path, 'r', encoding='utf-8') as file:
            file = PysFileBuffer(file, path)

    except FileNotFoundError:
        parser.error(f"can't open file {path!r}: No such file or directory")

    except PermissionError:
        parser.error(f"can't open file {path!r}: Permission denied.")

    except IsADirectoryError:
        parser.error(f"can't open file {path!r}: Path is not a file.")

    except NotADirectoryError:
        parser.error(f"can't open file {path!r}: Attempting to access directory from file.")

    except (OSError, IOError):
        parser.error(f"can't open file {path!r}: Attempting to access a system directory or file.")

    except UnicodeDecodeError:
        parser.error(f"can't read file {path!r}: Bad file.")

    except BaseException as e:
        parser.error(f"file {path!r}: Unexpected error: {e}")

    if args.highlight:
        try:
            print(
                pys_highlight(
                    file,
                    HLFMT_HTML if args.highlight == 'html' else HLFMT_ANSI
                )
            )
        except BaseException as e:
            parser.error(f"file {path!r}: Tokenize error: {e}")

    else:
        symtab = build_symbol_table(file)
        symtab.set('__name__', '__main__')

        result = pys_runner(
            file=file,
            mode='exec',
            symbol_table=symtab,
            flags=flags
        )

        code = handle_execute(result)

        if args.inspect:
            code = pys_shell(
                globals=result.context.symbol_table,
                flags=result.context.flags
            )

elif args.command is not None:
    file = PysFileBuffer(args.command)

    symtab = build_symbol_table(file)
    symtab.set('__name__', '__main__')

    code = handle_execute(
        pys_runner(
            file=file,
            mode='exec',
            symbol_table=symtab,
            flags=flags
        )
    )

else:
    code = pys_shell(
        globals=undefined,
        flags=flags
    )

exit(code)