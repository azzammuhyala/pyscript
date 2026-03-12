import sys

if sys.platform == 'win32':
    from msvcrt import getch

else:
    from termios import tcgetattr, tcsetattr, TCSADRAIN
    from tty import setraw
    from sys import stdin

    def getch() -> bytes:
        fileDescriptor = stdin.fileno()
        oldSettings = tcgetattr(fileDescriptor)
        try:
            setraw(stdin.fileno())
            return stdin.read(1).encode()
        finally:
            tcsetattr(fileDescriptor, TCSADRAIN, oldSettings)