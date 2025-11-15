from ..exceptions import PysException, PysShouldReturn

from os import environ
from sys import stderr, __excepthook__

def print_display(value):
    if value is not None:
        print(repr(value))

def print_traceback(exc_type, exc_value, exc_tb):
    if not isinstance(exc_tb, PysException):
        raise TypeError('exc_tb must be a PysException instance')

    for line in exc_tb.string_traceback().splitlines():
        print(line, file=stderr)

def sys_excepthook(exc_type, exc_value, exc_tb):
    if (
        isinstance(exc_value, PysShouldReturn) and
        exc_value.result.error is not None
    ):
        print_traceback(None, None, exc_value.result.error)

    else:
        __excepthook__(exc_type, exc_value, exc_tb)

def thread_excepthook(args):
    sys_excepthook(args.exc_type, args.exc_value, args.exc_traceback)

if environ.get('PYSCRIPT_NO_EXCEPTHOOK', '1') == '1':
    import sys
    import threading

    sys.excepthook = sys_excepthook
    threading.excepthook = thread_excepthook