from .buffer import PysFileBuffer
from .context import PysContext
from .symtab import SymbolTable
from .lexer import PysLexer
from .parser import PysParser
from .validator import PysValidator
from .interpreter import PysInterpreter
from .utils import create_new_symbol_table, is_exception
from .pysbuiltins import undefined, license
from .version import __version__

import sys

def pys_exec(file, symbol_table=None, *, statement=True, throw_exit=False):
    if not isinstance(file, (str, PysFileBuffer)):
        raise TypeError("pys_exec(): file must be str or pyscript.core.buffer.PysFileBuffer")
    if not isinstance(symbol_table, (type(None), SymbolTable)):
        raise TypeError("pys_exec(): symbol_table must be None, dict, or pyscript.core.symtab.SymbolTable")

    try:

        if isinstance(file, str):
            file = PysFileBuffer(file)

        lexer = PysLexer(file)
        tokens, error = lexer.make_tokens()

        if error:
            print(error.generate_string_traceback(), file=sys.stderr)
            return 1, None

        parser = PysParser(tokens)
        ast = parser.parse(None if statement else parser.expr)

        if ast.error:
            print(ast.error.generate_string_traceback(), file=sys.stderr)
            return 1, None

        validator = PysValidator(file)
        error = validator.visit(ast.node)

        if error:
            print(error.generate_string_traceback(), file=sys.stderr)
            return 1, None

        context = PysContext('<program>', file)
        context.symbol_table = symbol_table or create_new_symbol_table()

        interpreter = PysInterpreter()
        result = interpreter.visit(ast.node, context)

        if result.error:
            code = 1
            exception = result.error.exception

            if is_exception(exception, SystemExit):
                if throw_exit:
                    raise exception
                code = exception.args[0] if len(exception.args) == 1 else exception.args

            print(result.error.generate_string_traceback(), file=sys.stderr)

            return code, None

        return 0, result.value.value

    except KeyboardInterrupt:
        print('KeyboardInterrupt', file=sys.stderr)
        return 1, None

def pys_eval(file, symbol_table=None):
    return pys_exec(file, symbol_table, statement=False)

def pys_shell():
    print("PyScript {} (1 September 2025, 20:00:00 UTC+8)".format(__version__))
    print("Python {}".format(sys.version))
    print('Type ".exit" to exit the program or type ".license" for more information.')

    symbol_table = create_new_symbol_table()

    while True:

        try:
            text = input('>>> ')
            stripped_text = text.strip()

            if stripped_text == '.exit':
                break

            elif stripped_text == '.license':
                license()

            elif stripped_text == '.reset':
                symbol_table = create_new_symbol_table()

            else:
                code, result = pys_exec(PysFileBuffer(text, '<pyscript-shell>'), symbol_table, throw_exit=True)
                if code == 0 and len(result) == 1 and result[0] is not undefined:
                    print(repr(result[0]))

        except KeyboardInterrupt:
            print('\nKeyboardInterrupt. Type ".exit" to exit the program.', file=sys.stderr)

        except EOFError:
            break

        except SystemExit as e:
            exit(e)