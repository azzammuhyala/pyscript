from ..constants import DEFAULT, BOLD, ITALIC, UNDER, STRIKET
from .constants import ANSI_NAMES_MAP

from collections.abc import Sequence, Iterator
from inspect import currentframe
from io import IOBase
from json import detect_encoding
from os.path import sep, abspath, normpath

setimuattr = object.__setattr__
delimuattr = object.__delattr__

def tostr(obj):
    if isinstance(obj, str):
        return obj.replace('\r\n', '\n').replace('\r', '\n')

    elif isinstance(obj, (bytes, bytearray)):
        return tostr(obj.decode(detect_encoding(obj), 'surrogatepass'))

    elif isinstance(obj, IOBase):
        if not obj.readable():
            raise TypeError("unreadable IO")
        return tostr(obj.read())

    elif isinstance(obj, Iterator):
        return '\n'.join(map(tostr, obj))

    elif isinstance(obj, BaseException):
        return tostr(str(obj))

    elif isinstance(obj, type) and issubclass(obj, BaseException):
        return ''

    elif callable(obj):
        lines = []
        while True:
            line = obj()
            if not line:
                break
            lines.append(tostr(line))
        return '\n'.join(lines)

    raise TypeError('not a string')

def join_with_conjunction(iterable, func=tostr, conjunction='and'):
    sequence = list(map(func, iterable))
    length = len(sequence)

    if length == 1:
        return sequence[0]
    elif length == 2:
        return f'{sequence[0]} {conjunction} {sequence[1]}'
    return f'{", ".join(sequence[:-1])}, {conjunction} {sequence[-1]}'

def space_indent(string, length):
    prefix = ' ' * length
    return '\n'.join(prefix + line for line in tostr(string).splitlines())

def acolor(arg, style=DEFAULT):
    styles = []

    if style & BOLD:
        styles.append('1')
    if style & ITALIC:
        styles.append('3')
    if style & UNDER:
        styles.append('4')
    if style & STRIKET:
        styles.append('9')

    style_ansi = f'\x1b[{";".join(styles)}m' if styles else ''

    if isinstance(arg, str):
        arg = arg.strip().lower()

    if arg in ANSI_NAMES_MAP:
        return f'{style_ansi}\x1b[{ANSI_NAMES_MAP[arg]}m'
    elif isinstance(arg, Sequence) and len(arg) == 3 and all(isinstance(c, (int, str)) for c in arg):
        return f'{style_ansi}\x1b[38;2;{";".join(map(str, arg))}m'

    raise TypeError("acolor(): arg is invalid for ansi color")

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

def normalize_path(*paths, absolute=True):
    path = normpath(sep.join(map(tostr, paths)))
    return abspath(path) if absolute else path

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

def is_object_of(obj, class_or_tuple):
    return (
        isinstance(obj, class_or_tuple) or
        (isinstance(obj, type) and issubclass(obj, class_or_tuple))
    )