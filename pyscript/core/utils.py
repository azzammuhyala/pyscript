from .constants import SYNTAX_FILE, TOKENS, DEFAULT_SYNTAX

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

import json
import sys

def is_exception(exception, cls):
    return (
        isinstance(exception, cls) or
        (isinstance(exception, type) and issubclass(exception, cls))
    )

def get_line_column_by_index(index, file):
    return file.text.count('\n', 0, index) + 1, index - file.text.rfind('\n', 0, index)

def format_highlighted_text_with_arrow(position, file):
    string = ''

    line_start, col_start = get_line_column_by_index(position.start, file)
    line_end, col_end = get_line_column_by_index(position.end, file)
    text = file.text

    is_point_on_newline = text[position.start:position.end] == '\n'

    start = text.rfind('\n', 0, position.start) + 1
    end = text.find('\n', start + 1)

    if end == -1:
        end = len(text)

    count = 1 if is_point_on_newline else line_end - line_start + 1

    for i in range(count):
        line = text[start:end].lstrip('\n')

        start_column = col_start - 1 if i == 0 else 0
        end_column = col_end - 1 if i == count - 1 else len(line)

        if count == 1:
            stripped_line = line.strip()
            stripped_length = len(line) - len(stripped_line)

            string += stripped_line + '\n'

            arrow = '^' * (1 if is_point_on_newline else end_column - start_column)

            if arrow:
                string += ' ' * ((start_column - stripped_length) if count == 1 else start_column)
                string += arrow + '\n'

        else:
            string += line + '\n'

            arrow = '^' * (1 if is_point_on_newline else end_column - start_column)

            if arrow:
                string += ' ' * start_column
                string += arrow + '\n'

        start = end
        end = text.find('\n', start + 1)

        if end == -1:
            end = len(text)

    return string.replace('\t', ' ')

def get_token_name_by_token_type(type):
    from .token import PysToken

    if isinstance(type, PysToken):
        type = type.type

    for name, token_type in TOKENS.items():
        if token_type == type:
            return name

    return '<UNKNOWN>'

def join_with_conjunction(elements, func=None, conjunction='and'):
    if func is None:
        func = str

    if len(elements) == 1:
        return func(elements[0])
    elif len(elements) == 2:
        return func(elements[0]) + ' ' + conjunction + ' ' + func(elements[1])

    result = ''

    for i, element in enumerate(elements):
        if i == len(elements) - 1:
            result += conjunction + ' ' + func(element)
        else:
            result += func(element) + ', '

    return result

def create_new_symbol_table():
    from .symtab import PysSymbolTable
    from .pysbuiltins import builtins_dict

    symtab = PysSymbolTable()
    symtab.set('__builtins__', builtins_dict.copy())

    return symtab

def load_syntax():
    with open(SYNTAX_FILE, 'r') as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise TypeError("data is not an object or dict")

    if 'keywords' not in data or 'builtins' not in data:
        raise ValueError("data must be only 'keywords' and 'builtins'")

    if not isinstance(data['keywords'], dict):
        raise TypeError("keywords is not an object or dict")

    if not isinstance(data['builtins'], dict):
        raise TypeError("builtins is not an object or dict")

    for keyword, new_keyword in data['keywords'].items():
        if not isinstance(keyword, str):
            raise TypeError(f"keywords: {keyword!r}: is not a string")
        if not isinstance(new_keyword, str):
            raise TypeError(f"keywords: {new_keyword!r}: is not a string")

        if keyword not in DEFAULT_SYNTAX['keywords'].keys():
            raise ValueError(f"keywords: no keyword named {keyword!r}")

        if not new_keyword.isidentifier():
            raise ValueError(f"keywords: {new_keyword!r}: keyword is not an identifier")

    for name, new_name in data['builtins'].items():
        if not isinstance(name, str):
            raise TypeError(f"builtins: {name!r}: is not a string")
        if not isinstance(new_name, str):
            raise TypeError(f"builtins: {new_name!r}: is not a string")

        if not name.isidentifier():
            raise ValueError(f"builtins: {name!r}: name is not an identifier")
        if not new_name.isidentifier():
            raise ValueError(f"builtins: {new_name!r}: name is not an identifier")

    data['keywords'] = DEFAULT_SYNTAX['keywords'] | data['keywords']

    return data

try:
    SYNTAX = load_syntax()
except BaseException as e:
    print("Error: can't load file {} (using default syntax): {}".format(SYNTAX_FILE, e), file=sys.stderr)
    SYNTAX = DEFAULT_SYNTAX