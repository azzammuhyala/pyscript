from .bases import Pys
from .buffer import PysFileBuffer
from .constants import DEFAULT
from .position import PysPosition
from .symtab import PysSymbolTable, PysClassSymbolTable

from typing import Optional

class PysContext(Pys):

    __slots__ = ('file', 'name', 'qualname', 'flags', 'symbol_table', 'parent', 'parent_entry_position')

    def __init__(
        self,
        *,
        file: PysFileBuffer,
        name: Optional[str] = None,
        qualname: Optional[str] = None,
        flags: Optional[int] = None,
        symbol_table: Optional[PysSymbolTable] = None,
        parent: Optional['PysContext'] = None,
        parent_entry_position: Optional[PysPosition] = None
    ) -> None:

        if flags is None and parent:
            flags = parent.flags

        self.file = file
        self.name = name
        self.qualname = qualname
        self.flags = DEFAULT if flags is None else flags
        self.symbol_table = symbol_table
        self.parent = parent
        self.parent_entry_position = parent_entry_position

class PysClassContext(PysContext):

    __slots__ = ()

    def __init__(
        self,
        *,
        name: str,
        symbol_table: PysClassSymbolTable,
        parent: PysContext,
        parent_entry_position: PysPosition
    ) -> None:

        qualname = parent.qualname
        super().__init__(
            file=parent.file,
            name=name,
            qualname=name if qualname is None else f'{qualname}.{name}',
            symbol_table=symbol_table,
            parent=parent,
            parent_entry_position=parent_entry_position
        )