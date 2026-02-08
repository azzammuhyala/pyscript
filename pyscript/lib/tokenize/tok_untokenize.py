from pyscript.core.checks import is_keyword, is_left_bracket, is_right_bracket
from pyscript.core.constants import TOKENS
from pyscript.core.mapping import SYMBOLS_TOKEN_MAP
from pyscript.core.utils.generic import get_any

def untokenize(iterable):
    iterable = tuple(iterable)

    parts = []
    last_identifier = False
    brackets_stack = 0

    for i, token in enumerate(iterable):
        type = token.type
        value = token.value

        if type == TOKENS['NULL']:
            break

        elif type == TOKENS['NEWLINE']:
            stack = (
                brackets_stack - 1
                if brackets_stack > 0 and is_right_bracket(get_any(iterable, i + 1, token).type) else
                brackets_stack
            )
            parts.append(f'\n{"    " * stack}')
            last_identifier = False

        elif type == TOKENS['KEYWORD']:
            parts.append(f'{" " if last_identifier else ""}{value}')
            last_identifier = True

        elif type == TOKENS['IDENTIFIER']:
            parts.append(f'${value}' if is_keyword(value) else f'{" " if last_identifier else ""}{value}')
            last_identifier = True

        elif type in (TOKENS['NUMBER'], TOKENS['STRING']):
            parts.append(f'{" " if last_identifier else ""}{value!r}')
            last_identifier = True

        elif type == TOKENS['COMMENT']:
            parts.append(f' #{value}')
            last_identifier = False

        elif type == TOKENS['NONE']:
            parts.append(token.position.file.text[token.position.start:token.position.end])
            last_identifier = True

        elif is_left_bracket(type):
            brackets_stack += 1
            parts.append(SYMBOLS_TOKEN_MAP[type])
            last_identifier = False

        elif is_right_bracket(type):
            if brackets_stack > 0:
                brackets_stack -= 1
            parts.append(SYMBOLS_TOKEN_MAP[type])
            last_identifier = False

        else:
            parts.append(SYMBOLS_TOKEN_MAP[type])
            last_identifier = False

    return ''.join(parts)