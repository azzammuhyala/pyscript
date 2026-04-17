from .string import normstr

import os

def getcwd() -> str:
    try:
        return os.getcwd()
    except:
        return '.'

def abspath(path: str) -> str:
    try:
        return os.path.abspath(path)
    except:
        return path

def base(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]

def extension(path: str) -> str:
    return os.path.splitext(path)[1]

def normpath(*paths, absolute: bool = True) -> str:
    path = os.path.normpath(os.path.sep.join(map(normstr, paths)))
    return abspath(path) if absolute else path