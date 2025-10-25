from .core.buffer import PysFileBuffer
from .core.constants import DEFAULT, OPTIMIZE
from .core.handlers import handle_execute
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, pys_highlight
from .core.runner import pys_runner, pys_shell
from .core.symtab import build_symbol_table
from .core.utils import normalize_path
from .core.version import __version__

from argparse import ArgumentParser

import sys
import os

parser = ArgumentParser(
    prog='{} -m pyscript'.format(os.path.splitext(os.path.basename(sys.executable))[0]),
    description="PyScript Launcher for Python Version {}".format('.'.join(map(str, sys.version_info)))
)

parser.add_argument(
    'file',
    type=str,
    nargs='?',
    default=None,
    help="file path"
)

parser.add_argument(
    '-v', '-V', '--version',
    action='version',
    version="PyScript {}".format(__version__),
)

parser.add_argument(
    '-c', '-C', '--command',
    type=str,
    default=None,
    help="execute PyScript from argument",
)

parser.add_argument(
    '-o', '-O', '--optimize',
    action='store_true',
    help="set optimize flag"
)

parser.add_argument(
    '-i', '-I', '--inspect',
    action='store_true',
    help="inspect interactively after running a file",
)

parser.add_argument(
    '-l', '-L', '--highlight',
    choices=('html', 'ansi'),
    default=None,
    help='generate PyScript highlight code from a file'
)

args = parser.parse_args()

if args.highlight and args.file is None:
    parser.error("-l, -L, --highlight: file path require")

code = 0
flags = DEFAULT

if args.optimize:
    flags |= OPTIMIZE

if args.file is not None:
    path = normalize_path(args.file)

    try:
        with open(path, 'r') as file:
            file = PysFileBuffer(file.read(), path)

    except FileNotFoundError:
        parser.error("can't open file {!r}: No such file or directory".format(path))

    except PermissionError:
        parser.error("can't open file {!r}: Permission denied.".format(path))

    except IsADirectoryError:
        parser.error("can't open file {!r}: Path is not a file.".format(path))

    except NotADirectoryError:
        parser.error("can't open file {!r}: Attempting to access directory from file.".format(path))

    except (OSError, IOError):
        parser.error("can't open file {!r}: Attempting to access a system directory or file.".format(path))

    except UnicodeDecodeError:
        parser.error("can't read file {!r}: Bad file.".format(path))

    except BaseException as e:
        parser.error("file {!r}: Unexpected error: {}".format(path, e))

    if args.highlight:
        try:
            print(pys_highlight(file, HLFMT_HTML if args.highlight == 'html' else HLFMT_ANSI))
        except BaseException as e:
            parser.error("file {!r}: Tokenize error: {}".format(path, e))

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
                symbol_table=result.context.symbol_table,
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
    code = pys_shell(flags=flags)

sys.exit(code)