from .bases import Pys
from .utils.decorators import immutable
from .utils.general import setimuattr, tostr

from io import IOBase

@immutable
class PysBuffer(Pys):
    __slots__ = ()

class PysFileBuffer(PysBuffer):

    __slots__ = ('text', 'name')

    def __init__(self, text, name=None):

        if isinstance(text, PysFileBuffer):
            name = tostr(text.name if name is None else name)
            text = tostr(text.text)

        elif isinstance(text, IOBase):
            name = tostr(text.name if name is None else name)
            text = tostr(text)

        else:
            name = '<string>' if name is None else tostr(name)
            text = tostr(text)

        setimuattr(self, 'text', text)
        setimuattr(self, 'name', name)

    def __repr__(self):
        return f'<FileBuffer from {self.name!r}>'