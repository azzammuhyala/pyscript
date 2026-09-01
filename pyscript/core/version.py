from .bases import Pys
from .cache import pys_sys
from .mapping import TAG_VERSION_MAP
from .utils.decorators import immutable, inheritable, singleton

from re import match as match_regex

__version__ = '1.13.4'
__date__ = '1 September 2026, 20:00 UTC+7'
__author__ = ('AzzamMuhyala',)

version = pys_sys.version = f'{__version__} ({__date__})'

@singleton
@immutable
@inheritable
class PysVersionInfo(Pys, tuple):

    __slots__ = ()

    def __new_singleton__(cls) -> 'PysVersionInfo':
        match = match_regex(r'^(\d+)\.(\d+)\.(\d+)((?:a|b|rc)(\d+)|\.(dev|post)(\d+))?$', __version__)
        if not match:
            raise ValueError(f"invalid format version: {__version__!r}")

        major, minor, micro, pre_full, pre_num1, pre_tag2, pre_num2 = match.groups()

        if pre_full:

            if pre_tag2:
                pre_num = int(pre_num2)
                pre_tag_full = TAG_VERSION_MAP[pre_tag2]
            else:
                pre_num = int(pre_num1)
                pre_tag_full = (
                    TAG_VERSION_MAP[pre_full[0]]
                    if pre_full.startswith(('a', 'b')) else
                    TAG_VERSION_MAP['rc']
                )

        else:
            pre_tag_full = pre_num = None

        global version_info
        version_info = pys_sys.version_info = tuple.__new__(
            cls,
            (int(major), int(minor), int(micro), pre_tag_full, pre_num)
        )
        return version_info

    @property
    def major(self) -> int:
        return self[0]

    @property
    def minor(self) -> int:
        return self[1]

    @property
    def micro(self) -> int:
        return self[2]

    @property
    def pre_tag(self) -> str | None:
        return self[3]

    @property
    def pre_num(self) -> int | None:
        return self[4]

    @property
    def release(self) -> tuple[int, int, int]:
        return self[0:3]

    def __lt__(self, other: tuple) -> bool:
        return self.release < other

    def __gt__(self, other: tuple) -> bool:
        return self.release > other

    def __le__(self, other: tuple) -> bool:
        return self.release <= other

    def __ge__(self, other: tuple) -> bool:
        return self.release >= other

    def __eq__(self, other: tuple) -> bool:
        return self.release == other

    def __ne__(self, other: tuple) -> bool:
        return self.release != other

    def __repr__(self) -> str:
        return (
            'VersionInfo('
                f'major={self.major!r}, '
                f'minor={self.minor!r}, '
                f'micro={self.micro!r}' +
                (
                    ''
                    if self.pre_tag is None else
                    ', '
                    f'pre_tag={self.pre_tag!r}, '
                    f'pre_num={self.pre_num!r}'
                ) +
            ')'
        )

PysVersionInfo()