with open('./test.pys', 'r') as file:
    source = file.read()

import pyscript
import sys

import subprocess
import pygments
import pygments.formatters as formatters

def pyscript_tester():
    result = pyscript.pys_exec(source, pyscript.undefined, pyscript.RETURN_RESULT)
    code, exit = result.end_process()
    if code != 0:
        sys.exit(code)

def pyscript_highlight_tester():
    lexer = pyscript.PygmentsPyScriptLexer()
    formatter = formatters.TerminalTrueColorFormatter(style=pyscript.PygmentsPyScriptStyle, full=True)
    result = pygments.highlight(source, lexer, formatter)
    sys.stdout.write(result)
    sys.stdout.flush()

def pyscript_doc():
    subprocess.run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>',
        encoding='utf-8'
    )

if __name__ == '__main__':
    pass