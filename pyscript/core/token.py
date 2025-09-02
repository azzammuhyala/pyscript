from .bases import Pys
from .utils import get_token_name_by_token_type, Iterable

class PysToken(Pys):

    def __init__(self, file, type, position, value=None):
        self.file = file
        self.type = type
        self.position = position
        self.value = value

    def __repr__(self):
        return (
            'PysToken(' +
            get_token_name_by_token_type(self.type) +
            (', ' + repr(self.value) if self.value is not None else "") +
            ')'
        )

    def match(self, type, value):
        if not isinstance(value, Iterable):
            value = (value,)

        return self.type == type and self.value in value