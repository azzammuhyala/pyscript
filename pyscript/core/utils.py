from .constants import TOKENS, KEYWORDS

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from inspect import currentframe
from json import detect_encoding
from io import IOBase

import operator
import sys
import os

inplace_functions_map = {
    TOKENS['EPLUS']: operator.iadd,
    TOKENS['EMINUS']: operator.isub,
    TOKENS['EMUL']: operator.imul,
    TOKENS['EDIV']: operator.itruediv,
    TOKENS['EFDIV']: operator.ifloordiv,
    TOKENS['EPOW']: operator.ipow,
    TOKENS['EAT']: operator.imatmul,
    TOKENS['EMOD']: operator.imod,
    TOKENS['EAND']: operator.iadd,
    TOKENS['EOR']: operator.ior,
    TOKENS['EXOR']: operator.ixor,
    TOKENS['ELSHIFT']: operator.ilshift,
    TOKENS['ERSHIFT']: operator.irshift
}

keyword_identifiers_map = {
    KEYWORDS['true']: True,
    KEYWORDS['false']: False,
    KEYWORDS['none']: None
}

parenthesises_sequence_map = {
    'tuple': TOKENS['LPAREN'],
    'list': TOKENS['LSQUARE'],
    'dict': TOKENS['LBRACE'],
    'set': TOKENS['LBRACE']
}

parenthesises_map = {
    TOKENS['LPAREN']: TOKENS['RPAREN'],
    TOKENS['LSQUARE']: TOKENS['RSQUARE'],
    TOKENS['LBRACE']: TOKENS['RBRACE']
}

left_parenthesises = set(parenthesises_map.keys())
right_parenthesises = set(parenthesises_map.values())
parenthesises = left_parenthesises | right_parenthesises

highlight_keyword_identifiers = {
    KEYWORDS['of'], KEYWORDS['in'], KEYWORDS['is'],
    KEYWORDS['and'], KEYWORDS['or'], KEYWORDS['not'],
    KEYWORDS['False'], KEYWORDS['None'], KEYWORDS['True'],
    KEYWORDS['false'], KEYWORDS['none'], KEYWORDS['true']
}

builtins_blacklist = {'compile', 'copyright', 'credits', 'dir', 'eval', 'exec', 'globals', 'license', 'locals', 'vars'}

def to_str(obj):
    if isinstance(obj, str):
        return obj.replace('\r\n', '\n').replace('\r', '\n')

    elif isinstance(obj, (bytes, bytearray)):
        return to_str(obj.decode(detect_encoding(obj), 'surrogatepass'))

    elif isinstance(obj, IOBase):
        if not obj.readable():
            raise TypeError("unreadable IO")
        return to_str(obj.read())

    elif isinstance(obj, BaseException):
        return to_str(str(obj))

    elif isinstance(obj, type) and issubclass(obj, BaseException):
        return ''

    raise TypeError('not a string')

def join_with_conjunction(iterable, func=to_str, conjunction='and'):
    sequence = list(map(func, iterable))
    length = len(sequence)

    if length == 1:
        return sequence[0]
    elif length == 2:
        return '{} {} {}'.format(sequence[0], conjunction, sequence[1])

    return '{}, {} {}'.format(', '.join(sequence[:-1]), conjunction, sequence[-1])

def space_indent(string, length):
    prefix = ' ' * length
    return '\n'.join(prefix + line for line in to_str(string).splitlines())

def normalize_path(*paths, absolute=True):
    path = os.path.normpath(os.path.sep.join(map(to_str, paths)))
    if absolute:
        return os.path.abspath(path)
    return path

def is_object_of(obj, class_or_tuple):
    return isinstance(obj, class_or_tuple) or (isinstance(obj, type) and issubclass(obj, class_or_tuple))

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

def get_locals(deep=1):
    frame = currentframe()

    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1

    return (frame.f_locals if isinstance(frame.f_locals, dict) else dict(frame.f_locals)) if frame else {}

def supported_method(pyfunc, object, name, *args, **kwargs):
    from .handlers import handle_call
    from .singletons import undefined

    method = getattr(object, name, undefined)
    if method is undefined:
        return False, None

    if callable(method):
        code = pyfunc.__code__
        handle_call(method, code.context, code.position)

        try:
            result = method(*args, **kwargs)
            if result is NotImplemented:
                return False, None
            return True, result
        except NotImplementedError:
            return False, None

    return False, None

def print_display(value):
    if value is not None:
        print(repr(value))

def print_traceback(exception):
    for line in exception.string_traceback().splitlines():
        print(line, file=sys.stderr)