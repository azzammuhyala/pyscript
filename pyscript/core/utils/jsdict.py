from .generic import dsetitem, ddelitem, ditems

from typing import Any

def jsset(self: 'jsdict', key: Any, value: Any) -> None:
    if value is None:
        if key in self:
            ddelitem(self, key)
    else:
        dsetitem(self, key, value)

def jsdel(self: 'jsdict', key: Any) -> None:
    if key in self:
        ddelitem(self, key)

class jsdict(dict):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for key, value in tuple(ditems(self)):
            if value is None:
                ddelitem(self, key)

    def __repr__(self) -> str:
        return f'jsdict({super().__repr__()})'

    __getitem__ = __getattribute__ = dict.get
    __setitem__ = __setattr__ = jsset
    __delitem__ = __delattr__ = jsdel