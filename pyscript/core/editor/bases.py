from ..bases import Pys
from ..buffer import PysFileBuffer
from ..constants import CONFIGURATIONS_PATH
from ..utils.decorators import typecheck, inheritable
from ..utils.generic import setimuattr
from ..utils.string import normstr

from json import dump, load
from typing import Any

import os

class PysEditor(Pys):

    @typecheck
    def __init__(self, file: PysFileBuffer, colored: bool = True) -> None:
        self.file = file
        self.colored = bool(colored)
        self.basename = os.path.basename(self.file.name)
        self.used = False
        self.modified = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        inheritable(cls)

    def load_configuration(self) -> None:
        try:
            with open(CONFIGURATIONS_PATH, 'r', encoding='utf-8') as file:
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
        if configuration in self.configurations:
            return self.configurations[configuration]
        self.configurations[configuration] = default
        return default

    def set_configuration(self, configuration: str, value: Any) -> None:
        self.configurations[configuration] = value

    def save_configuration(self) -> None:
        try:
            with open(CONFIGURATIONS_PATH, 'w', encoding='utf-8') as file:
                dump(self.configurations, file, separators=(',', ':'))
        except:
            pass

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