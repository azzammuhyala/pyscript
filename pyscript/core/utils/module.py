from .path import extension

import os
import sys

def get_module_path(path: str) -> str | None:
    # circular import problem solved
    from ..checks import is_python_extension

    if os.path.isfile(path) and not is_python_extension(extension(path)):
        return path

    candidate = path + '.pys'
    if os.path.isfile(candidate):
        return candidate

    candidate = os.path.join(path, '__init__.pys')
    if os.path.isdir(path) and os.path.isfile(candidate):
        return candidate

def set_python_path(path: str) -> None:
    if path not in sys.path:
        sys.path.insert(0, path)

def remove_python_path(path: str) -> None:
    if path in sys.path:
        sys.path.remove(path)