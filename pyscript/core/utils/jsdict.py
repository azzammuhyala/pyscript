from .generic import dinit, drepr, dor, dsetitem, ddelitem, ditems

from typing import Any

class jsdict(dict):

    def __init__(self, *args, **kwargs) -> None:
        dinit(self, *args, **kwargs)
        for key, value in ditems(self):
            if value is None:
                ddelitem(self, key)

    def __repr__(self) -> str:
        return f'jsdict({drepr(self)})'

    def __or__(self, *args, **kwargs) -> 'jsdict':
        return jsdict(dor(self, *args, **kwargs))

    def __setattr__(self: 'jsdict', key: Any, value: Any) -> None:
        if value is None:
            if key in self:
                ddelitem(self, key)
        else:
            dsetitem(self, key, value)

    def __delattr__(self: 'jsdict', key: Any) -> None:
        if key in self:
            ddelitem(self, key)

    __getitem__ = __getattribute__ = dict.get
    __setitem__ = __setattr__
    __delitem__ = __delattr__