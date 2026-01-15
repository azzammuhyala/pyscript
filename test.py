with open('test.pys', 'r') as file:
    source = file.read()

import pyscript
import sys

from subprocess import run
from pygments import highlight
from pygments.formatters import HtmlFormatter, TerminalFormatter, TerminalTrueColorFormatter, Terminal256Formatter

def pyscript_tester():
    result = pyscript.pys_exec(source, pyscript.undefined, pyscript.RETURN_RESULT)
    code, exit = result.end_process()
    if code != 0:
        sys.exit(code)

lexer = pyscript.PygmentsPyScriptLexer()

def pyscript_highlight_tester():
    formatter = TerminalTrueColorFormatter(style=pyscript.PygmentsPyScriptStyle, full=True)
    result = highlight(source, lexer, formatter)
    print(result)

def pyscript_doc():
    run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>',
        encoding='utf-8'
    )

if __name__ == '__main__':
    pass