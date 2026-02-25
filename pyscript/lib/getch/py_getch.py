import sys

if sys.platform == 'win32':
    from msvcrt import getch

else:
    from termios import tcgetattr, tcsetattr, TCSADRAIN
    from tty import setraw

    def getch():
        standarInput = sys.stdin
        fileDescriptor = standarInput.fileno()
        oldSettings = tcgetattr(fileDescriptor)
        try:
            setraw(standarInput.fileno())
            return standarInput.read(1).encode()
        finally:
            tcsetattr(fileDescriptor, TCSADRAIN, oldSettings)