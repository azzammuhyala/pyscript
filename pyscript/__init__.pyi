from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from .core.buffer import PysFileBuffer
    from .core.symtab import PysSymbolTable

    from io import IOBase

from . import core

__version__: str
__all__: list[str]

def pys_exec(
    file: Union[str, IOBase, PysFileBuffer],
    symbol_table: Optional[Union[dict[str, Any], PysSymbolTable]] = None
) -> None: ...

def pys_eval(
    file: Union[str, IOBase, PysFileBuffer],
    symbol_table: Optional[Union[dict[str, Any], PysSymbolTable]] = None
) -> Any: ...