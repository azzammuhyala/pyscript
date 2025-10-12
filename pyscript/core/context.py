from .bases import Pys

class PysContext(Pys):

    def __init__(self, file, name=None, qualname=None, symbol_table=None, parent=None, parent_entry_position=None):
        self.file = file
        self.name = name
        self.qualname = qualname
        self.symbol_table = symbol_table
        self.parent = parent
        self.parent_entry_position = parent_entry_position

    def __repr__(self):
        return '<Context {!r}>'.format(self.name)