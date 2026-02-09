source = """
func add(a, b) {
    result = a + b
    breakpoint()
    return result
}

a = 1
b = 1

result = add(a, b)
print(result)
"""

import pyscript
import sys

from subprocess import run
from pygments import highlight
from pygments.formatters import HtmlFormatter

def pyscript_tester(filename=None):
    result = pyscript.pys_exec(
        pyscript.core.buffer.PysFileBuffer(source.strip(), filename),
        pyscript.undefined, pyscript.RETURN_RESULT
    )
    code, exit = result.end_process()
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
    print('PyScript version:', pyscript.version)
    pyscript_tester('pyscript.pys')
    pyscript_doc()