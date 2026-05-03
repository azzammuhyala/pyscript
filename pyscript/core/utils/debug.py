from ..constants import ENV_PYSCRIPT_NO_EXCEPTHOOK, ENV_PYSCRIPT_NO_READLINE
from ..exceptions import PysTraceback, PysSignal
from .generic import is_environ

from subprocess import run
from sys import excepthook
from types import TracebackType
from typing import Any, Literal

import sys

def print_display(value: Any) -> None:
    if value is not None:
        print(repr(value))

def print_traceback(exc_type: type[BaseException], exc_value: BaseException | None, exc_tb: PysTraceback) -> None:
    for line in exc_tb.string_traceback().splitlines():
        print(line, file=sys.stderr)

def sys_excepthook(exc_type: type[BaseException], exc_value: BaseException | None, exc_tb: TracebackType) -> None:
    if exc_type is PysSignal and (traceback := exc_value.result.error) is not None:
        print_traceback(None, None, traceback)
        print('\nThe above PyScript exception was the direct cause of the following exception:\n', file=sys.stderr)
    excepthook(exc_type, exc_value, exc_tb)

def thread_excepthook(args: Any) -> None:
    sys_excepthook(args.exc_type, args.exc_value, args.exc_traceback)

def import_readline() -> Literal[False]:
    return False

USE_NOTEBOOK = False

try:
    from IPython import get_ipython
    if type(get_ipython()).__name__ in (
        'ZMQInteractiveShell',     # Jupyter Notebook / Lab
        'Shell',                   # Google Colab
        'TerminalInteractiveShell' # IPython Terminal
    ):
        from IPython.display import clear_output
        def clear_shell() -> None:
            clear_output()
        USE_NOTEBOOK = True
except:
    pass

if USE_NOTEBOOK:
    pass

elif sys.platform == 'win32':
    def clear_shell() -> None:
        run('cls', shell=True)

else:
    def clear_shell() -> None:
        run('clear', shell=True)

    if not is_environ(ENV_PYSCRIPT_NO_READLINE):
        def import_readline() -> bool:
            try:
                import readline
                return True
            except:
                return False

def get_traceback_info(traceback: PysTraceback | None) -> tuple[type[BaseException] | None,
                                                                BaseException | None,
                                                                PysTraceback | None]:
    return (None, None, None) if traceback is None else (
        (exception, None, traceback)
        if isinstance(exception := traceback.exception, type) else
        (type(exception), exception, traceback)
    )

if not is_environ(ENV_PYSCRIPT_NO_EXCEPTHOOK):
    import threading

    sys.excepthook = sys_excepthook
    threading.excepthook = thread_excepthook