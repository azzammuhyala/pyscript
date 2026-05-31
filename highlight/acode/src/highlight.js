// PyScript 1.13.0+

const constantKeywords = [
    '__debug__', 'False', 'None', 'True', 'and', 'class', 'constructor', 'extends', 'func', 'function', 'false',
    'global', 'in', 'instanceof', 'is', 'not', 'nil', 'none', 'null', 'of', 'or', 'true', 'typeof'
];

const controlKeywords = [
    'as', 'assert', 'break', 'case', 'catch', 'continue', 'default', 'del', 'delete', 'do', 'elif', 'else', 'elseif',
    'except', 'finally', 'for', 'from', 'if', 'import', 'match', 'raise', 'repeat', 'return', 'switch', 'throw', 'try',
    'until', 'while', 'with'
];

const builtinTypes = [
    'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BaseExceptionGroup', 'BlockingIOError',
    'BrokenPipeError', 'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
    'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'EncodingWarning',
    'EnvironmentError', 'Exception', 'ExceptionGroup', 'FileExistsError', 'FileNotFoundError', 'FloatingPointError',
    'FutureWarning', 'GeneratorExit', 'IOError', 'ImportCycleError', 'ImportError', 'ImportWarning', 'IndexError',
    'InterruptedError', 'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError',
    'ModuleNotFoundError', 'NameError', 'NotADirectoryError', 'NotImplementedError', 'OSError', 'OverflowError',
    'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError', 'PythonFinalizationError', 'RecursionError',
    'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration', 'StopIteration',
    'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TimeoutError', 'TypeError', 'UnboundLocalError',
    'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning',
    'UserWarning', 'ValueError', 'Warning', 'WindowsError', 'ZeroDivisionError', 'bool', 'bytearray', 'bytes',
    'classmethod', 'complex', 'dict', 'enumerate', 'filter', 'float', 'frozendict', 'frozenset', 'int', 'list', 'map',
    'memoryview', 'object', 'property', 'range', 'reversed', 'set', 'slice', 'staticmethod', 'str', 'super', 'tuple',
    'type', 'zip'
];

const builtinFunctions = [
    'abs', 'aiter', 'all', 'anext', 'any', 'ascii', 'bin', 'breakpoint', 'callable', 'ce', 'chr', 'comprehension',
    'copyright', 'credits', 'decrement', 'delattr', 'dir', 'divmod', 'eval', 'exec', 'exit', 'format', 'getattr',
    'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'increment', 'input', 'isinstance', 'isobjectof', 'issubclass',
    'iter', 'len', 'license', 'locals', 'max', 'min', 'nce', 'next', 'oct', 'open', 'ord', 'pow', 'print', 'pyimport',
    'quit', 'repr', 'require', 'round', 'setattr', 'sorted', 'sum', 'unpack', 'vars'
];

const keywords = constantKeywords.concat(controlKeywords).join('|');
const integer = '[0-9](?:_?[0-9])*';
const scientific = `(?:[eE][+-]?${integer})`;
const imaginary = '[jJiI]?';
const dollar = '(?:\\$(?:[^\\S\\r\\n]*))?';
const identifier = '[a-zA-Z_][a-zA-Z0-9_]*';
const follow_identifier = `(\\s+)(?!(?:${keywords})\\b)(${dollar}${identifier})\\b`;
const raw_string_prefixes = '((?:R|r|BR|RB|Br|rB|Rb|bR|br|rb))';
const string_or_bytes_prefixes = '((?:B|b)?)';

export const extensions = ['pys'];

export const highlightRules = {

    'start': [
        // Strings
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: raw_string_prefixes + `(''')`,
            next: 'raw_string_apostrophe_triple'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: raw_string_prefixes + `(""")`,
            next: 'raw_string_quotation_triple'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: string_or_bytes_prefixes + `(''')`,
            next: 'string_apostrophe_triple'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: string_or_bytes_prefixes + `(""")`,
            next: 'string_quotation_triple'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: raw_string_prefixes + `(')`,
            next: 'raw_string_apostrophe_single'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: raw_string_prefixes + `(")`,
            next: 'raw_string_quotation_single'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: string_or_bytes_prefixes + `(')`,
            next: 'string_apostrophe_single'
        },
        {
            token: ['storage.type.string.prefix', 'punctuation.definition.string.begin'],
            regex: string_or_bytes_prefixes + `(")`,
            next: 'string_quotation_single'
        },

        // Numbers
        {
            token: ['storage.type.number', 'constant.numeric.bin', 'storage.type.imaginary.number'],
            regex: `\\b(0[bB])([01](?:_?[01])*)(${imaginary})\\b`
        },
        {
            token: ['storage.type.number', 'constant.numeric.oct', 'storage.type.imaginary.number'],
            regex: `\\b(0[oO])([0-7](?:_?[0-7])*)(${imaginary})\\b`
        },
        {
            token: ['storage.type.number', 'constant.numeric.hex', 'storage.type.imaginary.number'],
            regex: `\\b(0[xX])([0-9a-fA-F](?:_?[0-9a-fA-F])*)(${imaginary})\\b`
        },
        {
            token: ['constant.numeric.float', 'storage.type.imaginary.number'],
            regex: `(?<![\\w.])((?:(?:${integer})?\\.${integer}|${integer}\\.)${scientific}?)(${imaginary})(?![\\w.])`
        },
        {
            token: ['constant.numeric.float', 'storage.type.imaginary.number'],
            regex: `\\b(${integer}${scientific})(${imaginary})\\b`
        },
        {
            token: ['constant.numeric.integer', 'storage.type.imaginary.number'],
            regex: `\\b(${integer})(${imaginary})\\b`
        },

        // Comments
        {
            token: 'comment',
            regex: /#.*$/
        },

        // Identifiers
        {
            token: ['constant.language', 'text', 'storage.type'],
            regex: '\\b(class)\\b' + follow_identifier
        },
        {
            token: ['constant.language', 'text', 'storage.function'],
            regex: '\\b(func|function)\\b' + follow_identifier
        },
        {
            token: 'keyword.control',
            regex: `\\b(${controlKeywords.join('|')})\\b`
        },
        {
            token: 'constant.language',
            regex: `\\b(${constantKeywords.join('|')})\\b`
        },
        {
            token: 'support.type',
            regex: `${dollar}\\b(?:${builtinTypes.join('|')})\\b`
        },
        {
            token: 'support.function',
            regex: `${dollar}\\b(?:${builtinFunctions.join('|')})\\b`
        },
        {
            token: 'function',
            regex: `${dollar}\\b${identifier}\\b(?=\\s*\\()`
        },
        {
            token: 'constant.variable',
            regex: `${dollar}\\b(?:[A-Z_]*[A-Z][A-Z0-9_]*)\\b`
        },
        {
            token: 'variable',
            regex: `${dollar}\\b${identifier}\\b`
        },

        // Punctuations
        {
            token: 'punctuation.operator',
            regex: /[\(\),;\[\]{}]|\\$/
        },
        {
            token: 'keyword.operator',
            regex: '\\.\\.\\.|&&|\\*\\*|\\+\\+|--|//|<<|==|>>|\\?\\?|\\|\\||!=|%=|&=|\\*=|\\+=|-=|/=|:=|<=|>=|@=|^=|' +
                   '\\|=|~=|\\*\\*=|//=|<<=|>>=|->|=>|!>|~!|<>|[!%&\\*\\+\\-\\./:<=>\\?@^\\|~]'
        },

        // Errors
        {
            token: 'invalid.illegal',
            regex: /\\./
        },
        {
            token: 'invalid.illegal',
            regex: /\$(?:[^\S\r\n]*).?/
        }
    ],

    'raw_string_apostrophe_triple': [
        { include: 'raw-string-escapes' },
        { token: 'string', regex: /\\$/},
        { token: 'punctuation.definition.string.end', regex: /'''/, next: 'start' },
        { defaultToken: 'string.quoted.triple' }
    ],
    'raw_string_quotation_triple': [
        { include: 'raw-string-escapes' },
        { token: 'string', regex: /\\$/},
        { token: 'punctuation.definition.string.end', regex: /"""/, next: 'start' },
        { defaultToken: 'string.quoted.triple' }
    ],
    'string_apostrophe_triple': [
        { include: 'string-escapes' },
        { token: 'constant.character.escape', regex: /\\$/},
        { token: 'punctuation.definition.string.end', regex: /'''/, next: 'start' },
        { defaultToken: 'string.quoted.triple' }
    ],
    'string_quotation_triple': [
        { include: 'string-escapes' },
        { token: 'constant.character.escape', regex: /\\$/},
        { token: 'punctuation.definition.string.end', regex: /"""/, next: 'start' },
        { defaultToken: 'string.quoted.triple' }
    ],
    'raw_string_apostrophe_single': [
        { include: 'raw-string-escapes' },
        { token: 'string', regex: /\\$/, next: 'raw_string_apostrophe_single' },
        { token: 'invalid.illegal.unclosed-string', regex: /$/, next: 'start' },
        { token: 'punctuation.definition.string.end', regex: /'/, next: 'start' },
        { defaultToken: 'string.quoted.single' }
    ],
    'raw_string_quotation_single': [
        { include: 'raw-string-escapes' },
        { token: 'string', regex: /\\$/, next: 'raw_string_quotation_single' },
        { token: 'invalid.illegal.unclosed-string', regex: /$/, next: 'start' },
        { token: 'punctuation.definition.string.end', regex: /"/, next: 'start' },
        { defaultToken: 'string.quoted.single' }
    ],
    'string_apostrophe_single': [
        { include: 'string-escapes' },
        { token: 'constant.character.escape', regex: /\\$/, next: 'string_apostrophe_single' },
        { token: 'invalid.illegal.unclosed-string', regex: /$/, next: 'start' },
        { token: 'punctuation.definition.string.end', regex: /'/, next: 'start' },
        { defaultToken: 'string.quoted.single' }
    ],
    'string_quotation_single': [
        { include: 'string-escapes' },
        { token: 'constant.character.escape', regex: /\\$/, next: 'string_quotation_single' },
        { token: 'invalid.illegal.unclosed-string', regex: /$/, next: 'start' },
        { token: 'punctuation.definition.string.end', regex: /"/, next: 'start' },
        { defaultToken: 'string.quoted.single' }
    ],

    'raw-string-escapes': [
        { token: 'string', regex: /\\["'\\]/ }
    ],
    'string-escapes': [
        { token: 'constant.character.escape', regex: /\\[nrtbfav"'\\]/ },
        { token: 'constant.character.escape.octal', regex: /\\[0-7]{1,3}/ },
        { token: 'constant.character.escape.hex', regex: /\\x[0-9A-Fa-f]{2}/ },
        { token: 'constant.character.escape.unicode', regex: /\\u[0-9A-Fa-f]{4}/ },
        { token: 'constant.character.escape.unicode', regex: /\\U[0-9A-Fa-f]{8}/ },
        { token: 'constant.character.escape.unicode-name', regex: /\\N\{[^}]+\}/ },
        { token: 'invalid.illegal.escape', regex: /\\./ }
    ]
};