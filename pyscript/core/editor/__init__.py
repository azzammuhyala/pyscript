"""
All Editor Application Implementations for PyScript.

Not all editors are loaded (lazy import).
"""

from ..utils.path import normpath

from importlib import import_module as _import
from os.path import dirname
from pkgutil import iter_modules

__all__ = tuple(frozenset(
    name for _, name, _ in
    iter_modules((dirname(normpath(__file__)),))
))

def __getattr__(name: str):
    g = globals()
    if name in g:
        return g[name]
    elif name in __all__:
        module = _import(f'{__name__}.{name}')
        g[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__() -> list[str]:
    return sorted(tuple(globals().keys()) + __all__)

del normpath, iter_modules, dirname