from .bases import Pys
from .utils import print_traceback
from .version import __version__

from . import cache, version

_singletons = {}

class PysSingleton(Pys):

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

class PysUndefinedType(PysSingleton):

    __slots__ = ()

    def __new__(cls):
        if not isinstance(_singletons.get('undefined', None), PysUndefinedType):
            global undefined
            _singletons['undefined'] = undefined = super().__new__(cls)

        return _singletons['undefined']

    def __repr__(self):
        return 'undefined'

    def __bool__(self):
        return False

class PysVersionInfo(PysSingleton, tuple):

    __slots__ = ()

    def __new__(cls):
        if not isinstance(_singletons.get('version_info', None), PysVersionInfo):
            _singletons['version_info'] = version.version_info = super().__new__(cls, map(int, __version__.split('.')))

        return _singletons['version_info']

    def __repr__(self):
        return 'VersionInfo(major={!r}, minor={!r}, micro={!r})'.format(self.major, self.minor, self.micro)

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1]

    @property
    def micro(self):
        return self[2]

class PysHook(PysSingleton):

    __slots__ = ()

    def __new__(cls):
        if not isinstance(_singletons.get('hook', None), PysHook):
            _singletons['hook'] = cache.hook = self = super().__new__(cls)

            self.display = None
            self.exception = print_traceback
            self.ps1 = '>>> '
            self.ps2 = '... '

        return _singletons['hook']

    def __repr__(self):
        return '<hook object at {:016X}>'.format(id(self))

    @property
    def display(self):
        return _singletons['hook.display']

    @display.setter
    def display(self, value):
        if value is not None and not callable(value):
            raise TypeError("sys.hook.display: must be callable")
        _singletons['hook.display'] = value

    @property
    def exception(self):
        return _singletons['hook.exception']

    @exception.setter
    def exception(self, value):
        if value is not None and not callable(value):
            raise TypeError("sys.hook.exception: must be callable")
        _singletons['hook.exception'] = value

    @property
    def ps1(self):
        return _singletons['hook.ps1']

    @ps1.setter
    def ps1(self, value):
        if not isinstance(value, str):
            raise TypeError("sys.hook.ps1: must be a string")
        _singletons['hook.ps1'] = value

    @property
    def ps2(self):
        return _singletons['hook.ps2']

    @ps2.setter
    def ps2(self, value):
        if not isinstance(value, str):
            raise TypeError("sys.hook.ps2: must be a string")
        _singletons['hook.ps2'] = value

PysUndefinedType()
PysVersionInfo()
PysHook()