import pyscript

def pyscript_doc():
    import subprocess
    import html

    getch = pyscript.pys_require('getch')

    HIGHLIGHT_MAP = pyscript.core.mapping.HIGHLIGHT_MAP
    formatter = pyscript.core.highlight.PysHighlightFormatter(
        lambda position, content: pyscript.core.utils.string.normstr(html.escape(content)).replace('\n', '<br>'),
        lambda position, type: f'<span class="c-{type if type in HIGHLIGHT_MAP else "default"}">',
        lambda position, type: '</span>',
    )

    try:
        getch.init()

        while True:
            print('WAITING PASTE SOURCE OR INTTERUPT...', end='', flush=True)
            source = getch.getach(getch.getwch)
            print()
            if source == '\x03':
                print('EXITING...')
                break
            while getch.kbhit():
                source += getch.getach(getch.getwch)

            subprocess.run(
                args='clip',
                text=True,
                input=f'<div class="pys-code"><pre>{pyscript.pys_highlight(source, formatter)}</pre></div>',
                encoding=pyscript.pys_sys.encoding
            )
            print('COPYED TO CLIPBOARD')

    finally:
        getch.quit()

def update_snippets():
    import json

    with open('highlight/vscode/snippets/pyscript.json') as file:
        data = json.load(file)

    with open('highlight/acode/src/snippets.js', 'w') as file:
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

pyscript_doc()