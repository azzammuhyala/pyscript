from .path import getcwd, extension, normpath

import os
import sys

# circular import problem solved
is_python_extension = frozenset([
    '.cgi', '.fcgi', '.gyp', '.gypi', '.ipy', '.lmi', '.pxd', '.pxi', '.py', '.py3', '.pyc', '.pyd', '.pyde', '.pyi',
    '.pyo', '.pyp', '.pyproj', '.pyt', '.pyw', '.pyx', '.pyz', '.rpy', '.spec', '.tac', '.wsgi', '.xpy'
]).__contains__

def get_module_candidate(path: str, entry: str = '__init__') -> str | None:
    if os.path.isfile(path) and not is_python_extension(extension(path)):
        return path

    candidate = path + '.pys'
    if os.path.isfile(candidate):
        return candidate

    candidate = os.path.join(path, f'{entry}.pys')
    if os.path.isdir(path) and os.path.isfile(candidate):
        return candidate

def find_module_path(filename: str | None, name: str, entry: str = '__init__') -> tuple[str | None, str | None]:
    # circular import problem solved
    from ..cache import pys_sys

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