import pyscript

def pyscript_doc():
    import subprocess

    with open('./test.pys', 'r') as file:
        source = file.read()

    subprocess.run(
        args='clip',
        text=True,
        input=f'<pre>{pyscript.pys_highlight(source.strip())}</pre>',
        encoding=pyscript.pys_sys.encoding
    )

def update_snippets():
    import json

    with open('./highlight/vscode/snippets/pyscript.json') as file:
        data = json.load(file)

    with open('./highlight/acode/src/snippets.js', 'w') as file:
        content = []

        for name, snippet in data.items():
            prefix = snippet['prefix']
            body = snippet['body']
            if isinstance(body, list):
                body = '\n'.join(body)
            body = pyscript.core.utils.string.indent(body, 1, '\t')
            content.append(f'snippet {prefix}\n{body}')

        content = '\n\n'.join(content) + '\n'
        content = content.replace('\t', '\\t').replace('$', '\\$')
        file.write(f'export const snippets = `{content}`;')