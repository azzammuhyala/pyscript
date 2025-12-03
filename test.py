source = """

"""

import pyscript

from subprocess import run

def pyscript_tester():
    result = pyscript.pys_exec(source, pyscript.undefined, pyscript.RETRES)
    code = pyscript.core.handlers.handle_execute(result)
    if code != 0:
        exit(code)

def pyscript_doc():
    run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>'
    )

if __name__ == '__main__':
    pass