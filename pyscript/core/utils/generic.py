from inspect import currentframe
from types import FrameType, UnionType
from typing import Any, Optional, Sequence

import os

getattribute = object.__getattribute__
setimuattr = object.__setattr__
delimuattr = object.__delattr__
dinit = dict.__init__
drepr = dict.__repr__
dor = dict.__or__
dcontains = dict.__contains__
dgetitem = dict.__getitem__
dsetitem = dict.__setitem__
ddelitem = dict.__delitem__
dget = dict.get
dkeys = dict.keys
ditems = dict.items

def get_frame(deep: int = 0) -> FrameType | None:
    deep += 1
    frame = currentframe()
    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1
    return frame

def get_locals(deep: int = 0) -> dict[str, Any]:
    frame = get_frame(deep + 1)
    if frame:
        locals = frame.f_locals
        return locals if isinstance(locals, dict) else dict(locals)
    return {}

def get_sequence(object: Sequence, key: Any, default: Optional[Any] = None) -> Any:
    try:
        return object[key]
    except LookupError:
        return default

def is_environ(key: str) -> bool:
    return os.environ.get(key) is not None

def is_object_of(obj: object | type, class_or_tuple: type | UnionType | tuple[type | UnionType, ...]) -> bool:

    """
    Returns whether an object is derived from a parent class.
    The object here can be an initialized object, which calls `isinstance(obj, class_or_type)`,
    or a class type, which calls `issubclass(obj, class_or_tuple)`.
    """

    return (
        isinstance(obj, class_or_tuple) or
        (isinstance(obj, type) and issubclass(obj, class_or_tuple))
    )