from pyscript.core.checks import is_keyword
from pyscript.core.constants import TOKENS, KEYWORDS

SYMBOLS_TOKEN_MAPPING = {
    TOKENS['NOT-IN']: KEYWORDS['not'] + ' ' + KEYWORDS['in'],
    TOKENS['IS-NOT']: KEYWORDS['is'] + ' ' + KEYWORDS['not'],
    TOKENS['NULL']: '\0',
    TOKENS['NEWLINE']: '\n',
    TOKENS['EXCLAMATION']: '!',
    TOKENS['COMMENT']: '#',
    TOKENS['PERCENT']: '%',
    TOKENS['AMPERSAND']: '&',
    TOKENS['RIGHT-PARENTHESIS']: ')',
    TOKENS['LEFT-PARENTHESIS']: '(',
    TOKENS['STAR']: '*',
    TOKENS['PLUS']: '+',
    TOKENS['COMMA']: ',',
    TOKENS['MINUS']: '-',
    TOKENS['DOT']: '.',
    TOKENS['SLASH']: '/',
    TOKENS['COLON']: ':',
    TOKENS['SEMICOLON']: ';',
    TOKENS['LESS-THAN']: '<',
    TOKENS['EQUAL']: '=',
    TOKENS['GREATER-THAN']: '>',
    TOKENS['QUESTION']: '?',
    TOKENS['AT']: '@',
    TOKENS['LEFT-SQUARE']: '[',
    TOKENS['RIGHT-SQUARE']: ']',
    TOKENS['CIRCUMFLEX']: '^',
    TOKENS['LEFT-CURLY']: '{',
    TOKENS['PIPE']: '|',
    TOKENS['RIGHT-CURLY']: '}',
    TOKENS['TILDE']: '~',
    TOKENS['DOUBLE-AMPERSAND']: '&&',
    TOKENS['DOUBLE-STAR']: '**',
    TOKENS['DOUBLE-PLUS']: '++',
    TOKENS['DOUBLE-MINUS']: '--',
    TOKENS['DOUBLE-SLASH']: '//',
    TOKENS['DOUBLE-LESS-THAN']: '<<',
    TOKENS['DOUBLE-EQUAL']: '==',
    TOKENS['DOUBLE-GREATER-THAN']: '>>',
    TOKENS['DOUBLE-QUESTION']: '??',
    TOKENS['DOUBLE-PIPE']: '||',
    TOKENS['TRIPLE-DOT']: '...',
    TOKENS['EQUAL-EXCLAMATION']: '!=',
    TOKENS['EQUAL-PERCENT']: '%=',
    TOKENS['EQUAL-AMPERSAND']: '&=',
    TOKENS['EQUAL-STAR']: '*=',
    TOKENS['EQUAL-PLUS']: '+=',
    TOKENS['EQUAL-MINUS']: '-=',
    TOKENS['EQUAL-SLASH']: '/=',
    TOKENS['EQUAL-COLON']: ':=',
    TOKENS['EQUAL-LESS-THAN']: '<=',
    TOKENS['EQUAL-GREATER-THAN']: '>=',
    TOKENS['EQUAL-AT']: '@=',
    TOKENS['EQUAL-CIRCUMFLEX']: '^=',
    TOKENS['EQUAL-PIPE']: '|=',
    TOKENS['EQUAL-TILDE']: '~=',
    TOKENS['EQUAL-DOUBLE-STAR']: '**=',
    TOKENS['EQUAL-DOUBLE-SLASH']: '//=',
    TOKENS['EQUAL-DOUBLE-LESS-THAN']: '<<=',
    TOKENS['EQUAL-DOUBLE-GREATER-THAN']: '>>=',
    TOKENS['EXCLAMATION-TILDE']: '~!'
}

def untokenize(iterable):
    tokens = []

    for token in iterable:
        type = token.type
        value = token.value

        if type == TOKENS['NULL']:
            break
        elif type == TOKENS['KEYWORD']:
            tokens.append(value)
        elif type == TOKENS['IDENTIFIER']:
            tokens.append(f'${value}' if is_keyword(value) else value)
        elif type in (TOKENS['NUMBER'], TOKENS['STRING']):
            tokens.append(repr(value))
        else:
            tokens.append(SYMBOLS_TOKEN_MAPPING[type])

    return ' '.join(tokens)