source = """
func greet(name) {
    print("Hello, " + name + "!")
}

greet("Azzam")
"""

import pyscript

from subprocess import run
from html import escape

def pyscript_tester():
    result = pyscript.pys_eval(source, pyscript.undefined, pyscript.RETRES)
    code = pyscript.core.handlers.handle_execute(result)
    if code != 0:
        exit(code)

def pyscript_doc():
    formatter = pyscript.core.highlight._HighlightFormatter(
        lambda position, content: '<br>'.join(escape(content).splitlines()),
        lambda position, type: '<span id="{}">'.format(type),
        lambda position, type: '</span>',
        lambda position: '<br>'
    )

    run(
        args='clip',
        text=True,
        input='<pre class="pyscript-code">' + pyscript.pys_highlight(source.strip(), pyscript.HLFMT_HTML) + '</pre>'
    )

if __name__ == '__main__':
    pass