from .bases import Pys
from .checks import is_equal
from .cache import PysUndefined, undefined
from .mapping import GET_BINARY_FUNCTION
from .token import TOKENS
from .utils.decorators import immutable
from .utils.generic import setimuattr, dcontains, dgetitem, dsetitem, ddelitem, dget, dkeys
from .utils.similarity import get_closest

from types import ModuleType
from typing import Any, Optional

@immutable
class PysSymbolTable(Pys):

    __slots__ = ('parent', 'symbols', 'globals', 'builtins')

    def __init__(self, parent: Optional['PysSymbolTable'] = None) -> None:
        setimuattr(self, 'parent', parent.parent if isinstance(parent, PysClassSymbolTable) else parent)
        setimuattr(self, 'symbols', {})
        setimuattr(self, 'globals', set())

    def get(self, name: str) -> Any | PysUndefined:
        value = dget(self.symbols, name, undefined)

        if value is undefined:
            parent = self.parent
            if parent:
                return parent.get(name)

            builtins = getattr(self, 'builtins', undefined)
            if builtins is not undefined:
                return dget(builtins, name, undefined)

        return value

    def set(self, name: str, value: Any, *, operand: int = TOKENS['EQUAL']) -> bool:
        if is_equal(operand):
            if name in self.globals and (parent := self.parent):
                return parent.set(name, value, operand=operand)
            dsetitem(self.symbols, name, value)
            return True

        elif not dcontains(symbols := self.symbols, name):
            return (
                parent.set(name, value, operand=operand)
                if name in self.globals and (parent := self.parent) else
                False
            )

        dsetitem(symbols, name, GET_BINARY_FUNCTION(operand)(dgetitem(symbols, name), value))
        return True

    def remove(self, name: str) -> bool:
        symbols = self.symbols

        if not dcontains(symbols, name):
            return (
                parent.remove(name)
                if name in self.globals and (parent := self.parent) else 
                False
            )

        ddelitem(symbols, name)
        return True

class PysClassSymbolTable(PysSymbolTable):

    __slots__ = ()

    def __init__(self, parent: PysSymbolTable) -> None:
        super().__init__(parent)

def find_closest(symbol_table: PysSymbolTable, name: str) -> str | None:
    symbols = set(dkeys(symbol_table.symbols))
    update = symbols.update

    parent = symbol_table.parent
    while parent:
        update(dkeys(parent.symbols))
        symbol_table = parent
        parent = parent.parent

    builtins = getattr(symbol_table, 'builtins', undefined)
    if builtins is not undefined:
        update(dkeys(builtins))

    return get_closest(symbols, name)

def new_module_namespace(
    *,
    symbols: dict | None = None,
    **kwargs
) -> tuple[PysSymbolTable, ModuleType | None]:

    # circular import problem solved
    from .pysbuiltins import pys_builtins

    dict_builtins = pys_builtins.__dict__
    symbol_table = PysSymbolTable()

    if symbols is None:
        module = ModuleType(kwargs['name'], kwargs.get('doc'))
        setimuattr(symbol_table, 'symbols', module.__dict__)
        setimuattr(symbol_table, 'builtins', dict_builtins)
        symbol_table.set('__builtins__', pys_builtins)
        symbol_table.set('__file__', kwargs['file'])

    else:
        module = None
        builtins = dget(symbols, '__builtins__', undefined)
        setimuattr(symbol_table, 'symbols', symbols)
        if builtins is undefined:
            setimuattr(symbol_table, 'builtins', dict_builtins)
            symbol_table.set('__builtins__', dict_builtins)
        else:
            setimuattr(
                symbol_table, 'builtins',
                builtins if isinstance(builtins, dict) else getattr(builtins, '__dict__', dict_builtins)
            )

    return symbol_table, module