from ..constants import ENV_PYSCRIPT_NO_EXCEPTHOOK, ENV_PYSCRIPT_NO_READLINE
from ..exceptions import PysSignal

from os import environ, system
from sys import excepthook

import sys

def print_display(value):
    if value is not None:
        print(repr(value))

def print_traceback(exc_type, exc_value, exc_tb):
    for line in exc_tb.string_traceback().splitlines():
        print(line, file=sys.stderr)

def sys_excepthook(exc_type, exc_value, exc_tb):
    if exc_type is PysSignal and (traceback := exc_value.result.error) is not None:
        print_traceback(None, None, traceback)
        print('\nThe above PyScript exception was the direct cause of the following exception:\n', file=sys.stderr)
    excepthook(exc_type, exc_value, exc_tb)

def thread_excepthook(args):
    sys_excepthook(args.exc_type, args.exc_value, args.exc_traceback)

def import_readline():
    return False

if 'google.colab' in sys.modules:
    from google.colab.output import clear
    def clear_shell():
        clear()

elif sys.platform == 'win32':
    def clear_shell():
        system('cls')

else:
    def clear_shell():
        system('clear')

    if environ.get(ENV_PYSCRIPT_NO_READLINE) is None:
        def import_readline():
            try:
                import readline
                return True
            except:
                return False

def get_error_args(traceback):
    return (None, None, None) if traceback is None else (
        (exception, None, traceback)
        if isinstance(exception := traceback.exception, type) else
        (type(exception), exception, traceback)
    )

if environ.get(ENV_PYSCRIPT_NO_EXCEPTHOOK) is None:
    import threading
    sys.excepthook = sys_excepthook
    threading.excepthook = thread_excepthook