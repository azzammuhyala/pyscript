from ..bases import Pys
from ..buffer import PysFileBuffer
from ..utils.decorators import inheritable
from ..utils.generic import setimuattr
from ..utils.string import normstr

from os.path import basename

class PysEditor(Pys):

    __slots__ = ('file', 'used', 'modified', 'wrapped', 'basename')

    def __init__(self, file: PysFileBuffer) -> None:
        self.file = file
        self.used = False
        self.modified = False
        self.wrapped = True
        self.basename = basename(self.file.name)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        inheritable(cls)

    def save(self, text) -> None:
        text = normstr(text)
        with open(self.file.name, 'w', encoding='utf-8') as file:
            file.write(text)
            setimuattr(self.file, 'text', text)
        self.modified = False

    def run(self) -> None:
        if self.used:
            raise RuntimeError("one application object can only be used once")
        self.used = True