with open('./test.pys', 'r') as file:
    source = file.read()

import sys
import subprocess
import pyscript
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

def update_snippets():
    import json

    with open('./highlight/vscode/snippets/pyscript.json') as file:
        data = json.load(file)

    with open('./highlight/acode/src/snippets.js', 'w') as file:
        content = []

        for name, snippet in data.items():
            # type = name.split(' - ')[0].lower()
            prefix = snippet['prefix']
            body = snippet['body']
            if isinstance(body, list):
                body = '\n'.join(body)
            body = pyscript.core.utils.string.indent(body, 1, '\t')
            content.append(f'snippet {prefix}\n{body}')

        content = '\n\n'.join(content) + '\n'
        content = content.replace('\t', '\\t').replace('$', '\\$')
        file.write(f'export const snippets = `{content}`;')
