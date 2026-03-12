from os import getcwd as osgetcwd
from os.path import sep, abspath as osabspath, normpath as osnormpath, splitext, basename

from .string import normstr

def getcwd() -> str:
    try:
        return osgetcwd()
    except:
        return '.'

def abspath(path: str) -> str:
    try:
        return osabspath(path)
    except:
        return path

def base(path: str) -> str:
    return splitext(basename(path))[0]

def extension(path: str) -> str:
    return splitext(basename(path))[1]

def normpath(*paths, absolute: bool = True) -> str:
    path = osnormpath(sep.join(map(normstr, paths)))
    return abspath(path) if absolute else path

def get_name_from_path(path) -> str:
    return base(normpath(path, absolute=False))