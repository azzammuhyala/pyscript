from .bases import Pys
from .constants import TOKENS
from .cache import undefined
from .utils.constants import BINARY_FUNCTIONS_MAP
from .utils.decorators import immutable
from .utils.general import setimuattr, get_closest

from os.path import basename

@immutable
class PysSymbolTable(Pys):

    __slots__ = ('parent', 'symbols', 'globals')

    def __init__(self, parent=None):
        setimuattr(self, 'parent', parent.parent if isinstance(parent, PysClassSymbolTable) else parent)
        setimuattr(self, 'symbols', {})
        setimuattr(self, 'globals', set())

    def find_closest(self, name):
        symbols = set(self.symbols.keys())

        parent = self.parent
        while parent:
            symbols.update(parent.symbols.keys())
            parent = parent.parent

        builtins = self.get('__builtins__')
        if builtins is not undefined:
            symbols.update(
                (
                    builtins
                    if isinstance(builtins, dict) else
                    getattr(builtins, '__dict__', {})
                ).keys()
            )

        return get_closest(symbols, name)

    def get(self, name):
        value = self.symbols.get(name, undefined)

        if value is undefined:
            if self.parent:
                return self.parent.get(name)

            builtins = self.symbols.get('__builtins__', undefined)
            if builtins is not undefined:
                return (
                    builtins
                    if isinstance(builtins, dict) else
                    getattr(builtins, '__dict__', {})
                ).get(name, undefined)

        return value

    def set(self, name, value, operand=TOKENS['EQ']):
        if operand == TOKENS['EQ']:

            if name in self.globals and self.parent:
                success = self.parent.set(name, value, operand)
                if success:
                    return True

            self.symbols[name] = value
            return True

        if name not in self.symbols:
            if name in self.globals and self.parent:
                return self.parent.set(name, value, operand)
            return False

        self.symbols[name] = BINARY_FUNCTIONS_MAP[operand](self.symbols[name], value)
        return True

    def remove(self, name):
        if name not in self.symbols:
            if name in self.globals and self.parent:
                return self.parent.remove(name)
            return False

        del self.symbols[name]
        return True

class PysClassSymbolTable(PysSymbolTable):

    __slots__ = ()

    def __init__(self, parent):
        super().__init__(parent)

def build_symbol_table(file, globals=None):
    symtab = PysSymbolTable()

    if globals is None:
        symtab.set('__file__', file.name)
        symtab.set('__name__', basename(file.name))
    else:
        setimuattr(symtab, 'symbols', globals)

    if symtab.get('__builtins__') is undefined:
        from .pysbuiltins import pys_builtins
        symtab.set('__builtins__', pys_builtins)

    return symtab