from pyscript.core.buffer import PysFileBuffer
from pyscript.core.runner import pys_exec, pys_shell

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="run a pyscript file or shell")

    parser.add_argument(
        'file',
        type=str,
        nargs='?',
        default=None,
        help="executable pyscript file path"
    )

    args = parser.parse_args()

    if args.file is None:
        pys_shell()

    else:
        try:
            with open(args.file, 'r') as file:
                file = PysFileBuffer(file.read(), file.name)
        except FileNotFoundError:
            print(f"PyScript: can't open file '{args.file}': No such file or directory", file=sys.stderr)
            exit(2)
        except PermissionError:
            print(f"PyScript: can't open file '{args.file}': Permission denied.", file=sys.stderr)
            exit(2)
        except IsADirectoryError:
            print(f"PyScript: can't open file '{args.file}': Path is not a file.", file=sys.stderr)
            exit(2)
        except NotADirectoryError:
            print(f"PyScript: can't open file '{args.file}': Attempting to access directory from file.", file=sys.stderr)
            exit(2)
        except (OSError, IOError):
            print(f"PyScript: can't open file '{args.file}': Attempting to access a system directory or file.", file=sys.stderr)
            exit(2)
        except UnicodeDecodeError:
            print(f"PyScript: can't read file '{args.file}': Bad file.", file=sys.stderr)
            exit(2)
        except BaseException as e:
            print(f"PyScript: file '{args.file}': Unexpected error: {e}", file=sys.stderr)
            exit(2)

        exit(pys_exec(file)[0])

if __name__ == '__main__':
    main()
else:
    raise ImportError("pys.py: file is not a module")