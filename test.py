source = """

"""

import pyscript
import sys

from subprocess import run

def pyscript_tester():
    result = pyscript.pys_exec(source, pyscript.undefined, pyscript.RETRES)
    code, exit = result.process()
    if code != 0:
        sys.exit(code)

def pyscript_doc():
    run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>'
    )

if __name__ == '__main__':
    pass