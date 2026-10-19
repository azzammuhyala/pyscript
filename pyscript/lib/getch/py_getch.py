import sys

INITIALIZED = False

if sys.platform == 'win32':
    import msvcrt
    import signal

    OLD_INTERRUPT_HANDLER = None
    INTERRUPT = False

    def _interrupted(signum, frame):
        global INTERRUPT
        INTERRUPT = True

    def init() -> None:
        global INITIALIZED, OLD_INTERRUPT_HANDLER
        if INITIALIZED:
            return

        INITIALIZED = True
        OLD_INTERRUPT_HANDLER = signal.signal(signal.SIGINT, _interrupted)

    def quit() -> None:
        global INITIALIZED, OLD_INTERRUPT_HANDLER
        if not INITIALIZED:
            return

        signal.signal(signal.SIGINT, OLD_INTERRUPT_HANDLER)

        OLD_INTERRUPT_HANDLER = None
        INITIALIZED = False

    def kbhit() -> bool:
        return msvcrt.kbhit() or INTERRUPT

    def getch() -> bytes:
        global INTERRUPT
        if not INITIALIZED:
            raise Exception('not initialized')
        elif INTERRUPT:
            INTERRUPT = False
            return b'\x03'
        return msvcrt.getch()

else:
    import termios
    import select
    import tty
    import os

    FILE_DESCRIPTOR = None
    OLD_SETTINGS = None

    def init() -> None:
        global INITIALIZED, FILE_DESCRIPTOR, OLD_SETTINGS
        if INITIALIZED:
            return

        INITIALIZED = True
        FILE_DESCRIPTOR = sys.stdin.fileno()
        OLD_SETTINGS = termios.tcgetattr(FILE_DESCRIPTOR)
        tty.setraw(FILE_DESCRIPTOR)

    def quit() -> None:
        global INITIALIZED, FILE_DESCRIPTOR, OLD_SETTINGS
        if not INITIALIZED:
            return

        termios.tcsetattr(FILE_DESCRIPTOR, termios.TCSADRAIN, OLD_SETTINGS)

        FILE_DESCRIPTOR = None
        OLD_SETTINGS = None
        INITIALIZED = False

    def kbhit() -> bool:
        return bool(select.select((FILE_DESCRIPTOR,), (), (), 0)[0])

    def getch() -> bytes:
        if not INITIALIZED:
            raise Exception('not initialized')
        return os.read(FILE_DESCRIPTOR, 1)

def getwch() -> str:
    codes = getch()
    first = codes[0]
    if first >= 0xF0:   extra = 3
    elif first >= 0xE0: extra = 2
    elif first >= 0xC0: extra = 1
    else:               extra = 0
    for _ in range(extra):
        codes += getch()
    return codes.decode('utf-8', errors='replace')

def getach(f=getch) -> bytes | str:
    codes = f()
    while kbhit():
        codes += f()
    return codes