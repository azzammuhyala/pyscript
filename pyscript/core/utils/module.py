from ..cache import pys_sys
from .path import getcwd, extension, normpath

import os
import sys

def get_module_candidate(path: str, entry: str = '__init__') -> str | None:
    # circular import problem solved
    from ..checks import is_python_extension

    if os.path.isfile(path) and not is_python_extension(extension(path)):
        return path

    candidate = path + '.pys'
    if os.path.isfile(candidate):
        return candidate

    candidate = os.path.join(path, f'{entry}.pys')
    if os.path.isdir(path) and os.path.isfile(candidate):
        return candidate

def find_module_path(filename: str | None, name: str, entry: str = '__init__') -> tuple[str | None, str | None]:
    for path in pys_sys.path:
        path = normpath(path, name)
        module_path = get_module_candidate(path, entry)
        if module_path is not None:
            break
    else:
        path = normpath(os.path.dirname(filename or '') or getcwd(), name)
        module_path = get_module_candidate(path, entry)
        if module_path == filename:
            module_path = None

    return (None if module_path is None else path), module_path

def set_python_path(path: str) -> None:
    if path not in sys.path:
        sys.path.insert(0, path)

def remove_python_path(path: str) -> None:
    if path in sys.path:
        sys.path.remove(path)