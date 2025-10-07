import pyscript

source = """

"""

from subprocess import run
from html import escape

def pyscript_tester():
    result = pyscript.pys_exec(source, {}, pyscript.RETRES)
    code = pyscript.core.handlers.handle_execute(result)
    if code != 0:
        exit(code)

def pyscript_doc():
    formatter = pyscript.core.highlight._HighlightFormatter(
        lambda position, content: pyscript.core.utils.sanitize_newline('<br>', escape(content)),
        lambda position, type: '<span id="{}">'.format(type),
        lambda position, type: '</span>',
        lambda position: '<br>'
    )

    run(
        args='clip',
        text=True,
        input='<pre class="pyscript-code">' + pyscript.pys_highlight(source.strip(), formatter) + '</pre>'
    )

if __name__ == '__main__':
    pyscript_tester()
    pyscript_doc()