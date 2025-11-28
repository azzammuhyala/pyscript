from ..constants import DEFAULT, BOLD, ITALIC, UNDER, STRIKET

from collections.abc import Sequence, Iterator
from inspect import currentframe
from io import IOBase
from json import detect_encoding
from os.path import sep, abspath, basename, isdir, isfile, join, normcase, splitext
from sys import path as pypath

delimuattr = object.__delattr__
setimuattr = object.__setattr__

def normstr(obj):
    if isinstance(obj, str):
        return obj.replace('\r\n', '\n').replace('\r', '\n')
    elif isinstance(obj, (bytes, bytearray)):
        return normstr(obj.decode(detect_encoding(obj), 'surrogatepass'))
    elif isinstance(obj, IOBase):
        if not obj.readable():
            raise TypeError("unreadable IO")
        return normstr(obj.read())
    elif isinstance(obj, Iterator):
        return '\n'.join(map(normstr, obj))
    elif callable(obj):
        lines = []
        while True:
            line = obj()
            if not line:
                break
            lines.append(normstr(line))
        return '\n'.join(lines)

    raise TypeError('not a string')

def join_with_conjunction(iterable, func=normstr, conjunction='and'):
    sequence = list(map(func, iterable))
    length = len(sequence)

    if length == 1:
        return sequence[0]
    elif length == 2:
        return f'{sequence[0]} {conjunction} {sequence[1]}'
    return f'{", ".join(sequence[:-1])}, {conjunction} {sequence[-1]}'

def space_indent(string, length):
    prefix = ' ' * length
    return '\n'.join(prefix + line for line in normstr(string).splitlines())

def acolor(arg, style=DEFAULT):
    from ..mapping import ANSI_NAMES_MAP

    styles = []

    if style & BOLD:
        styles.append('1')
    if style & ITALIC:
        styles.append('3')
    if style & UNDER:
        styles.append('4')
    if style & STRIKET:
        styles.append('9')

    style = f'\x1b[{";".join(styles)}m' if styles else ''

    if isinstance(arg, str):
        arg = arg.strip().lower()

    if arg in ANSI_NAMES_MAP:
        return f'{style}\x1b[{ANSI_NAMES_MAP[arg]}m'
    elif isinstance(arg, Sequence) and len(arg) == 3 and all(isinstance(c, (int, str)) for c in arg):
        return f'{style}\x1b[38;2;{";".join(map(str, arg))}m'

    raise TypeError("acolor(): arg is invalid for ansi color")

def normpath(*paths, absolute=True):
    path = normcase(sep.join(map(normstr, paths)))
    return abspath(path) if absolute else path

def get_similarity_ratio(string1, string2):
    string1 = [char for char in string1.lower() if not char.isspace()]
    string2 = [char for char in string2.lower() if not char.isspace()]

    bigram1 = set(string1[i] + string1[i + 1] for i in range(len(string1) - 1))
    bigram2 = set(string2[i] + string2[i + 1] for i in range(len(string2) - 1))

    max_bigrams_count = max(len(bigram1), len(bigram2))

    return 0.0 if max_bigrams_count == 0 else len(bigram1 & bigram2) / max_bigrams_count

def get_closest(names, name, cutoff=0.6):
    best_match = None
    best_score = 0.0

    for element in (names if isinstance(names, set) else set(names)):
        score = get_similarity_ratio(name, element)
        if score >= cutoff and score > best_score:
            best_score = score
            best_match = element

    return best_match

def get_package_name(path):
    return splitext(basename(normpath(path, absolute=False)))[0]

def get_package(path, name):
    from ..checks import is_python_extensions

    package_path = normpath(path, name, absolute=False)
    if isfile(package_path) and not is_python_extensions(splitext(package_path)[1]):
        return package_path

    candidate = package_path + '.pys'
    if isfile(candidate):
        return candidate

    candidate = join(package_path, '__init__.pys')
    if isdir(package_path) and isfile(candidate):
        return candidate

def get_locals(deep=1):
    frame = currentframe()

    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1

    if frame:
        locals = frame.f_locals
        return locals if isinstance(locals, dict) else dict(locals)

    return {}

def get_error_args(exception):
    if exception is None:
        return None, None, None

    pyexception = exception.exception
    return (
        (pyexception, None, exception)
        if isinstance(pyexception, type) else
        (type(pyexception), pyexception, exception)
    )

def set_python_path(path):
    if path not in pypath:
        pypath.insert(0, path)

def is_object_of(obj, class_or_tuple):
    return (
        isinstance(obj, class_or_tuple) or
        (isinstance(obj, type) and issubclass(obj, class_or_tuple))
    )