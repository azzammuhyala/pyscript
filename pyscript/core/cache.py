from .bases import Pys
from .constants import LIBRARY_PATH
from .utils.decorators import uninherited, singleton
from .utils.debug import print_traceback

from os.path import splitext
from os import listdir
from threading import RLock

loading_modules = set()
singletons = dict()
modules = dict()
lock = RLock()

try:
    library = set(splitext(lib)[0] for lib in listdir(LIBRARY_PATH))
except BaseException as e:
    library = set()

@singleton
@uninherited
class PysUndefined(Pys):

    __slots__ = ()

    def __new_singleton__(cls):
        global undefined
        undefined = object.__new__(cls)
        return undefined

    def __repr__(self):
        return 'undefined'

    def __bool__(self):
        return False

@singleton
@uninherited
class PysHook(Pys):

    __slots__ = ()

    def __new_singleton__(cls):
        global hook
        hook = object.__new__(cls)
        hook.display = None
        hook.exception = print_traceback
        hook.ps1 = '>>> '
        hook.ps2 = '... '
        return hook

    def __repr__(self):
        return f'<hook object at {id(self):016X}>'

    @property
    def display(self):
        return singletons['hook.display']

    @display.setter
    def display(self, value):
        if value is not None and not callable(value):
            raise TypeError("sys.hook.display: must be callable")
        singletons['hook.display'] = value

    @property
    def exception(self):
        return singletons['hook.exception']

    @exception.setter
    def exception(self, value):
        if value is not None and not callable(value):
            raise TypeError("sys.hook.exception: must be callable")
        singletons['hook.exception'] = value

    @property
    def ps1(self):
        return singletons['hook.ps1']

    @ps1.setter
    def ps1(self, value):
        if not isinstance(value, str):
            raise TypeError("sys.hook.ps1: must be a string")
        singletons['hook.ps1'] = value

    @property
    def ps2(self):
        return singletons['hook.ps2']

    @ps2.setter
    def ps2(self, value):
        if not isinstance(value, str):
            raise TypeError("sys.hook.ps2: must be a string")
        singletons['hook.ps2'] = value

PysUndefined()
PysHook()