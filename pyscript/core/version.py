from .bases import Pys
from .utils.decorators import immutable, uninherited, singleton

__version__ = '1.5.1'
__date__ = '16 November 2025, 12:10 UTC+7'

version = f'{__version__} ({__date__})'

@singleton
@immutable
@uninherited
class PysVersionInfo(Pys, tuple):

    __slots__ = ()

    def __new_singleton__(cls):
        global version_info
        version_info = tuple.__new__(cls, map(int, __version__.split('.')))
        return version_info

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1]

    @property
    def micro(self):
        return self[2]

    def __repr__(self):
        return f'VersionInfo(major={self.major!r}, minor={self.minor!r}, micro={self.micro!r})'

PysVersionInfo()