from .bases import Pys

class PysContext(Pys):

    def __init__(self, name, file, parent_entry_position=None, parent=None):
        self.name = name
        self.file = file
        self.parent = parent
        self.parent_entry_position = parent_entry_position
        self.symbol_table = None