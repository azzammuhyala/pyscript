import pyperclip
import pyscript
import keyboard
import pynput
import html
import time

fpstimer = pyscript.pys_require('fpstimer>fpstimer')
formatter = pyscript.core.highlight.PysHighlightFormatter(
    lambda position, content: pyscript.core.utils.string.normstr(html.escape(content)).replace('\n', '<br>'),
    lambda position, type: f'<span class="c-{type if type in pyscript.core.mapping.HIGHLIGHT_MAP else "default"}">',
    lambda position, type: '</span>',
)

def on_click(x, y, button, pressed):
    if not (pressed and button == pynput.mouse.Button.middle):
        return

    keyboard.send('ctrl+x')
    time.sleep(0.3)
    pyperclip.copy(f'<div class="pys-code"><pre>{pyscript.pys_highlight(pyperclip.paste(), formatter)}</pre></div>')
    time.sleep(0.1)
    keyboard.send('ctrl+v')
    print('CONVERTED')

with pynput.mouse.Listener(on_click=on_click) as listener:
    print('READY')
    while True:
        fpstimer.tick(20)