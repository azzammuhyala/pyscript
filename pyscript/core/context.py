from .bases import Pys
from .constants import DEFAULT

class PysContext(Pys):

    def __init__(self, file, name=None, qualname=None, flags=None, symbol_table=None, parent=None, parent_entry_position=None):
        if flags is None and parent:
            flags = parent.flags

        self.file = file
        self.name = name
        self.qualname = qualname
        self.flags = DEFAULT if flags is None else flags
        self.symbol_table = symbol_table
        self.parent = parent
        self.parent_entry_position = parent_entry_position

    def __repr__(self):
        return '<Context {!r}>'.format(self.name)