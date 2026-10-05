from ..bases import Pys
from ..buffer import PysFileBuffer
from ..cache import pys_sys
from ..constants import CONFIGURATIONS_PATH
from ..utils.decorators import typecheck, inheritable
from ..utils.generic import delimuattr
from ..utils.string import normstr

from json import dump, load
from os.path import basename
from typing import Any

class PysEditor(Pys):

    @typecheck
    def __init__(self, file: PysFileBuffer, colored: bool = True) -> None:
        self.file = file
        self.colored = bool(colored)
        self.basename = basename(self.file.name)
        self.used = False
        self.modified = False

        self.load_configuration()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        inheritable(cls)

    def load_configuration(self) -> None:
        try:
            with open(CONFIGURATIONS_PATH, 'r', encoding=pys_sys.encoding) as file:
                result = load(file)
            if not isinstance(result, dict):
                raise ValueError
            for key in result:
                if not isinstance(key, str):
                    raise ValueError
            self.configurations = result
        except:
            self.configurations = {}

    def get_configuration(self, configuration: str, default: Any) -> Any:
        return self.configurations.setdefault(configuration, default)

    def set_configuration(self, configuration: str, value: Any) -> None:
        self.configurations[configuration] = value

    def save_configuration(self) -> None:
        try:
            with open(CONFIGURATIONS_PATH, 'w', encoding=pys_sys.encoding) as file:
                dump(self.configurations, file, separators=(',', ':'))
        except:
            pass

    def save(self, text) -> None:
        if not self.modified:
            return

        try:
            with open(self.file.name, 'w', encoding=pys_sys.encoding) as file:
                file.write(normstr(text))
        except:
            pass
        else:
            self.modified = False

    def run(self) -> None:
        if self.used:
            raise RuntimeError("one application object can only be used once")
        delimuattr(self.file, 'text')
        self.used = True