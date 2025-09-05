from .bases import Pys
from .constants import TOKENS

class PysSymbolTable(Pys):

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        from .singletons import undefined

        value = self.symbols.get(name, undefined)

        if value is undefined:
            if self.parent:
                return self.parent.get(name)

            builtins = self.symbols.get('__builtins__', undefined)

            if builtins is not undefined:
                if isinstance(builtins, dict):
                    return builtins.get(name, undefined)
                elif isinstance(builtins, PysSymbolTable):
                    return builtins.get(name)

        return value

    def set(self, name, value, operand=TOKENS['EQ']):
        if operand == TOKENS['EQ']:
            self.symbols[name] = value
            return True

        if not self.include(name):
            return False

        if operand == TOKENS['IPLUS']:
            self.symbols[name] += value
        elif operand == TOKENS['IMINUS']:
            self.symbols[name] -= value
        elif operand == TOKENS['IMUL']:
            self.symbols[name] *= value
        elif operand == TOKENS['IDIV']:
            self.symbols[name] /= value
        elif operand == TOKENS['IFDIV']:
            self.symbols[name] //= value
        elif operand == TOKENS['IPOW']:
            self.symbols[name] **= value
        elif operand == TOKENS['IMOD']:
            self.symbols[name] %= value
        elif operand == TOKENS['IAND']:
            self.symbols[name] &= value
        elif operand == TOKENS['IXOR']:
            self.symbols[name] ^= value
        elif operand == TOKENS['ILSHIFT']:
            self.symbols[name] <<= value
        elif operand == TOKENS['IRSHIFT']:
            self.symbols[name] >>= value

        return True

    def remove(self, name):
        if self.include(name):
            del self.symbols[name]
            return True
        return False

    def include(self, name):
        return name in self.symbols