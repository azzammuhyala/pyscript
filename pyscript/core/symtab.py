from .bases import Pys
from .values import PysValue

class SymbolTable(Pys):

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        from .pysbuiltins import undefined

        value = self.symbols.get(name, undefined)

        if value is undefined:
            if self.parent:
                return self.parent.get(name)

            builtins = self.symbols.get('__builtins__', undefined)

            if builtins is not undefined:
                if isinstance(builtins.value, dict):
                    result = builtins.value.get(name, undefined)
                    if result is not undefined:
                        return PysValue(result)

                elif isinstance(builtins.value, SymbolTable):
                    return builtins.value.get(name)

        return value

    def set(self, name, value):
        self.symbols[name] = PysValue(value)

    def remove(self, name):
        if name in self.symbols:
            del self.symbols[name]
            return True

        return False

    def clear(self):
        self.symbols.clear()

    def copy(self):
        symtab = type(self)(self.parent)

        for key, value in self.symbols.items():
            symtab.symbols[key] = value.copy()

        return symtab