with open('test.pys', 'r') as file:
    source = file.read()

import pyscript
import sys

from subprocess import run
from pygments import highlight
from pygments.formatters import HtmlFormatter

def pyscript_tester():
    result = pyscript.pys_exec(source, pyscript.undefined, pyscript.RETURN_RESULT)
    code, exit = result.process()
    if code != 0:
        sys.exit(code)

def pyscript_highlight_tester():
    lexer = pyscript.PygmentsPyScriptLexer()
    formatter = HtmlFormatter(full=True)
    result = highlight(source, lexer, formatter)
    with open('result.html', 'w') as file:
        file.write(result)

def pyscript_doc():
    run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>',
        encoding='utf-8'
    )

if __name__ == '__main__':
    pyscript_highlight_tester()