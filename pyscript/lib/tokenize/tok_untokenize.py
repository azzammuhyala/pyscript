from pyscript.core.checks import is_keyword, is_left_bracket, is_right_bracket
from pyscript.core.mapping import SYMBOLS_TOKEN_MAP
from pyscript.core.token import TOKENS, PysToken
from pyscript.core.utils.decorators import immutable, inheritable, singleton
from pyscript.core.utils.generic import get_subscript

from typing import Iterable

@immutable
@inheritable
@singleton
class TokenValueError:

    def __repr__(self):
        return '\\ERROR'

token_value_error = TokenValueError()

def untokenize(iterable: Iterable[PysToken]) -> str:
    iterable = tuple(iterable)

    parts = []
    add_space = False
    newline = True
    brackets_stack = 0

    for i, token in enumerate(iterable):
        type = token.type
        value = token.value

        if isinstance(value, tuple) and len(value) == 2 and callable(func := value[1]):
            try:
                value = func()
            except:
                value = token_value_error

        if type == TOKENS['NULL']:
            break

        elif type == TOKENS['NEWLINE']:
            stack = (
                brackets_stack - 1
                if brackets_stack > 0 and is_right_bracket(get_subscript(iterable, i + 1, token).type) else
                brackets_stack
            )
            parts.append(f'\n{"    " * stack}')
            newline = True
            add_space = False
            continue

        elif type == TOKENS['KEYWORD']:
            parts.append(f'{" " if add_space else ""}{value}')
            add_space = True

        elif type == TOKENS['IDENTIFIER']:
            parts.append(f'${value}' if is_keyword(value) else f'{" " if add_space else ""}{value}')
            add_space = True

        elif type in (TOKENS['NUMBER'], TOKENS['STRING']):
            parts.append(f'{" " if add_space else ""}{value!r}')
            add_space = True

        elif type == TOKENS['COMMENT']:
            parts.append(f'{"" if newline else " "}#{value}')
            add_space = False

        elif type == TOKENS['NONE']:
            parts.append(token.position.file.text[token.position.start:token.position.end])
            add_space = True

        elif is_left_bracket(type):
            brackets_stack += 1
            parts.append(SYMBOLS_TOKEN_MAP[type])
            add_space = False

        elif is_right_bracket(type):
            if brackets_stack > 0:
                brackets_stack -= 1
            parts.append(SYMBOLS_TOKEN_MAP[type])
            add_space = False

        else:
            parts.append(SYMBOLS_TOKEN_MAP[type])
            add_space = False

        newline = False

    return ''.join(parts)