from .cache import library, hook
from .constants import LIBRARY_PATH, TOKENS, KEYWORDS

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
    KEYWORDS['True']: True,
    KEYWORDS['False']: False,
    KEYWORDS['None']: None
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

def to_str(object):
    if isinstance(object, str):
        return object.replace('\r\n', '\n')

    elif isinstance(object, (bytes, bytearray)):
        return to_str(object.decode(detect_encoding(object), 'surrogatepass'))

    elif isinstance(object, IOBase):
        if not object.readable():
            raise TypeError("unreadable IO")
        return to_str(object.read())

    elif isinstance(object, BaseException):
        return to_str(str(object))

    elif isinstance(object, type) and issubclass(object, BaseException):
        return ''

    raise TypeError('not a string')

def join_with_conjunction(sequence, func=None, conjunction='and'):
    if func is None:
        func = to_str

    if len(sequence) == 1:
        return func(sequence[0])
    elif len(sequence) == 2:
        return func(sequence[0]) + ' ' + conjunction + ' ' + func(sequence[1])

    result = ''

    for i, element in enumerate(sequence):
        if i == len(sequence) - 1:
            result += conjunction + ' ' + func(element)
        else:
            result += func(element) + ', '

    return result

def space_indent(string, length):
    result = ''
    prefix = ' ' * length

    for line in to_str(string).splitlines(True):
        result += prefix + line

    return result

def normalize_path(*paths, absolute=True):
    path = os.path.normpath(os.path.sep.join(map(to_str, paths)))
    if absolute:
        return os.path.abspath(path)
    return path

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

def is_object_of(obj, class_or_tuple):
    return isinstance(obj, class_or_tuple) or (isinstance(obj, type) and issubclass(obj, class_or_tuple))

def supported_method(object, name, *args, **kwargs):
    from .singletons import undefined

    method = getattr(object, name, undefined)
    if method is undefined:
        return False, None

    if callable(method):
        try:
            result = method(*args, **kwargs)
            if result is NotImplemented:
                return False, None
            return True, result
        except NotImplementedError:
            return False, None

    return False, None

def build_symbol_table(file, globals=None):
    from .objects import PysModule
    from .singletons import undefined
    from .symtab import PysSymbolTable

    symtab = PysSymbolTable()

    symtab.module = PysModule(os.path.basename(file.name))

    if globals is not None:
        symtab.module.__dict__ = globals

    symtab.symbols = symtab.module.__dict__

    if symtab.get('__builtins__') is undefined:
        from .pysbuiltins import pys_builtins
        symtab.set('__builtins__', pys_builtins)

    if globals is None:
        symtab.set('__file__', file.name)

    return symtab

def print_display(value):
    if value is not None:
        print(repr(value))

def print_traceback(exception):
    for line in exception.string_traceback().splitlines():
        print(line, file=sys.stderr)

hook.exception = print_traceback

try:
    for lib in os.listdir(LIBRARY_PATH):
        library.add(os.path.splitext(lib)[0])
except BaseException as e:
    print("Error: cannot load library folder {}: {}".format(LIBRARY_PATH, e), file=sys.stderr)