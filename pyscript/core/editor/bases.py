from ..bases import Pys
from ..buffer import PysFileBuffer
from ..utils.decorators import typecheck, inheritable
from ..utils.generic import setimuattr
from ..utils.string import normstr

import os

class PysEditor(Pys):

    @typecheck
    def __init__(self, file: PysFileBuffer, colored: bool = True) -> None:
        self.file = file
        self.colored = bool(colored)
        self.used = False
        self.modified = False
        self.wrapped = True
        self.basename = os.path.basename(self.file.name)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        inheritable(cls)

    def save(self, text) -> None:
        try:
            text = normstr(text)
            with open(self.file.name, 'w', encoding='utf-8') as file:
                file.write(text)
                setimuattr(self.file, 'text', text)
        except:
            pass
        else:
            self.modified = False

    def run(self) -> None:
        if self.used:
            raise RuntimeError("one application object can only be used once")
        self.used = True