from .buffer import PysFileBuffer
from .exceptions import PysException
from .position import PysPositionRange
from .context import PysContext
from .symtab import PysSymbolTable
from .lexer import PysLexer
from .parser import PysParser
from .validator import PysValidator
from .interpreter import PysInterpreter
from .utils import create_new_symbol_table, is_exception
from .pysbuiltins import license
from .singletons import undefined
from .version import __version__, __date__

from io import IOBase

import sys

def pys_execute(source, mode, symbol_table=None, throw_exit=False):
    context = PysContext('<program>', source)

    try:
        lexer = PysLexer(source)
        tokens, error = lexer.make_tokens()

        if error:
            return error, None

        parser = PysParser(tokens)
        ast = parser.parse(None if mode == 'exec' else parser.expr)

        if ast.error:
            return ast.error, None

        validator = PysValidator(source)
        error = validator.visit(ast.node)

        if error:
            return error, None

        context.symbol_table = symbol_table or create_new_symbol_table()

        interpreter = PysInterpreter()
        result = interpreter.visit(ast.node, context)

        if result.error:
            if is_exception(result.error.exception, SystemExit) and throw_exit:
                raise result.error.exception

            return result.error, None

        return None, result.value

    except KeyboardInterrupt as e:
        return PysException(e, PysPositionRange(0, 0), context), None

def pys_exec(source, symbol_table=None):
    """
    Execute a PyScript code from source given.
    """

    if isinstance(source, str):
        source = PysFileBuffer(source)
    elif isinstance(source, IOBase):
        source = PysFileBuffer(source.read(), source.name)
        if not isinstance(source.text, str):
            raise TypeError("pys_exec(): IO from source must be read as str")
    elif not isinstance(source, PysFileBuffer):
        raise TypeError("pys_exec(): source must be str, IO object, or pyscript.core.buffer.PysFileBuffer")

    if isinstance(symbol_table, dict):
        if not all(isinstance(k, str) and k.isidentifier() for k in symbol_table.keys()):
            raise ValueError("pys_exec(): symbol_table found an invalid name")
        s = symbol_table
        symbol_table = create_new_symbol_table()
        symbol_table.symbols.update(s)
    elif not isinstance(symbol_table, (type(None), PysSymbolTable)):
        raise TypeError("pys_exec(): symbol_table must be dict or pyscript.core.symtab.PysSymbolTable")

    error, _ = pys_execute(source, mode='exec', symbol_table=symbol_table)

    if error:
        raise error.exception

def pys_eval(source, symbol_table=None):
    """
    Evaluate a PyScript code from source given.
    """

    if isinstance(source, str):
        source = PysFileBuffer(source)
    elif isinstance(source, IOBase):
        source = PysFileBuffer(source.read(), source.name)
        if not isinstance(source.text, str):
            raise TypeError("pys_eval(): IO from source must be read as str")
    elif not isinstance(source, PysFileBuffer):
        raise TypeError("pys_eval(): source must be str, IO object, or pyscript.core.buffer.PysFileBuffer")

    if isinstance(symbol_table, dict):
        if not all(isinstance(k, str) and k.isidentifier() for k in symbol_table.keys()):
            raise ValueError("pys_eval(): symbol_table found an invalid name")
        s = symbol_table
        symbol_table = create_new_symbol_table()
        symbol_table.symbols.update(s)
    elif not isinstance(symbol_table, (type(None), PysSymbolTable)):
        raise TypeError("pys_eval(): symbol_table must be dict or pyscript.core.symtab.PysSymbolTable")

    error, result = pys_execute(source, mode='eval', symbol_table=symbol_table)

    if error:
        raise error.exception

    return result

def pys_shell():
    print("PyScript {} ({})".format(__version__, __date__))
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
                error, result = pys_execute(PysFileBuffer(text, '<pyscript-shell>'), 'exec', symbol_table, throw_exit=True)

                if error:
                    print(error.generate_string_traceback(), file=sys.stderr)

                elif len(result) == 1 and result[0] is not undefined:
                    print(repr(result[0]))

        except KeyboardInterrupt:
            print('\nKeyboardInterrupt. Type ".exit" to exit the program.', file=sys.stderr)

        except EOFError:
            break

        except SystemExit as e:
            exit(e)