from .bases import Pys
from .utils import get_token_name_by_token_type

class PysToken(Pys):

    def __init__(self, type, position, value=None):
        self.type = type
        self.position = position
        self.value = value

    def __repr__(self):
        return 'Token({}{})'.format(
            get_token_name_by_token_type(self.type),
            '' if self.value is None else ', {!r}'.format(self.value)
        )

    def match(self, type, value):
        return self.type == type and self.value == value

    def matches(self, type, values):
        return self.type == type and self.value in values