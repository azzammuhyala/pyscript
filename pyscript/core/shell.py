from .bases import Pys
from .cache import pys_sys
from .mapping import BRACKETS_MAP

from typing import Literal

import sys

class PysIncompleteHandler(Pys):

    def __init__(self) -> None:
        self._brackets_stack = []
        self.reset()

    def is_multiline(self) -> bool:
        return not self._must_break and (
            len(self._brackets_stack) > 0 or
            self._next_line or
            self._is_triple_string or
            self._in_decorator
        )

    def reset(self) -> None:
        self._brackets_stack.clear()
        self._in_string = False
        self._in_decorator = False
        self._is_triple_string = False
        self._next_line = False
        self._must_break = False
        self._string_prefix = ''
        self.text = ''

    def process(self, text: str) -> bool:
        self._in_decorator = False
        self._next_line = False

        is_space = True
        index = 0

        while index < len(text):
            character = text[index]

            if character == '\\':
                index += 1
                character = text[index:index+1]

                if character == '':
                    self._next_line = True
                    break

            elif character in '\'"':
                bind_3 = text[index:index+3]

                if self._is_triple_string:
                    if len(bind_3) == 3 and self._string_prefix * 3 == bind_3:
                        self._in_string = False
                        self._is_triple_string = False
                        index += 2

                else:
                    if not self._in_string and bind_3 in ("'''", '"""'):
                        self._is_triple_string = True
                        index += 2

                    if self._in_string and self._string_prefix == character:
                        self._in_string = False
                    else:
                        self._string_prefix = character
                        self._in_string = True

            if not self._in_string:

                if character == '#':
                    break

                elif is_space and character == '@':
                    self._in_decorator = True
                    index += 1
                    continue

                elif character in '([{':
                    self._brackets_stack.append(ord(character))

                elif character in ')]}':
                    self._must_break = (
                        BRACKETS_MAP[self._brackets_stack.pop()] != ord(character)
                        if self._brackets_stack else
                        True
                    )

                if is_space and not character.isspace():
                    is_space = False

            index += 1

        if self._in_decorator and is_space:
            self._in_decorator = False
        if self._in_string and not (self._next_line or self._is_triple_string):
            self._must_break = True

        if self.is_multiline():
            self.text += text + '\n'
        else:
            self.text += text

class PysLineShell(PysIncompleteHandler):

    def __init__(self, ps1: str = '>>> ', ps2: str = '... ', colored: bool = True) -> None:
        super().__init__()
        self.colored = colored
        self.ps1 = ps1
        self.ps2 = ps2

    def process_command(self, text: str) -> Literal[0, 1, -1] | None:
        if text == '/exit':
            return 0
        elif text == '/clean':
            return 1
        elif text == '/clear':
            pys_sys.clearhook()
            return -1

    def prompt(self) -> Literal[0]:
        return 0

class PysClassicLineShell(PysLineShell):

    def prompt(self) -> str | Literal[0, 1]:
        while True:

            try:

                if self.is_multiline():
                    text = input(self.ps2)

                else:
                    text = input(self.ps1)
                    code = self.process_command(text)
                    if code == -1:
                        continue
                    elif code is not None:
                        return code

            except (OSError, ValueError):
                return 0

            except (MemoryError, UnicodeDecodeError):
                print("InputError", file=sys.stderr)
                continue

            self.process(text)

            if not self.is_multiline():
                text = self.text
                self.reset()
                return text

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.layout.processors import TabsProcessor
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.output.color_depth import ColorDepth
    from prompt_toolkit.styles.pygments import style_from_pygments_cls

    class PysPromptToolkitLineShell(PysLineShell, PromptSession):

        def __init__(self, ps1: str = '>>> ', ps2: str = '... ', colored: bool = True) -> None:
            # circular import problem solved
            from .highlight import PYGMENTS, PygmentsPyScriptStyle, PygmentsPyScriptShellLexer

            PysLineShell.__init__(self, ps1, ps2, colored)

            self.multiline_state = False
            self.overwrite = False

            self.key_bindings = KeyBindings()

            @self.key_bindings.add('tab', eager=True)
            def _(event):
                self.default_buffer.insert_text('\t')

            @self.key_bindings.add('insert', eager=True)
            def _(event):
                self.overwrite = not self.overwrite

            @self.key_bindings.add('pageup', eager=True)
            def _(event):
                self.default_buffer.cursor_position = 0

            @self.key_bindings.add('pagedown', eager=True)
            def _(event):
                buffer = self.default_buffer
                buffer.cursor_position = len(buffer.text)

            @self.key_bindings.add(Keys.Any)
            def _(event):
                buffer = self.default_buffer
                text = event.data
                if self.overwrite and buffer.cursor_position < len(buffer.text):
                    buffer.delete(1)
                    buffer.insert_text(text)
                else:
                    buffer.insert_text(text)

            style_keyword = {}

            if colored:
                if PYGMENTS:
                    style_keyword.update({
                        'lexer': PygmentsLexer(PygmentsPyScriptShellLexer),
                        'style': style_from_pygments_cls(PygmentsPyScriptStyle)
                    })
            else:
                style_keyword.update({
                    'color_depth': ColorDepth.DEPTH_1_BIT
                })

            PromptSession.__init__(
                self,
                multiline=Condition(lambda: self.multiline_state),
                input_processors=[TabsProcessor(tabstop=4)],
                key_bindings=self.key_bindings,
                prompt_continuation=lambda width, line_number, is_soft_wrap: self._ps2,
                **style_keyword
            )

            self.default_buffer.on_text_changed += self.on_multiline_state

        def prompt(self) -> str | Literal[0, 1]:
            while True:

                try:

                    text = PromptSession.prompt(self, self._ps1)

                    # Ctrl + Z
                    if text.startswith('\x1a'):
                        raise EOFError

                    elif '\n' not in text:
                        code = self.process_command(text)
                        if code == -1:
                            continue
                        elif code is not None:
                            return code

                    return text

                except (OSError, ValueError):
                    return 0

                except (MemoryError, UnicodeDecodeError):
                    print("InputError", file=sys.stderr)
                    continue

        @property
        def ps1(self) -> str:
            return self._ps1.value if self.colored else self._ps1

        @ps1.setter
        def ps1(self, value: str) -> None:
            self._ps1 = ANSI(value) if self.colored else value

        @property
        def ps2(self) -> str:
            return self._ps2.value if self.colored else self._ps2

        @ps2.setter
        def ps2(self, value: str) -> None:
            self._ps2 = ANSI(value) if self.colored else value

        def on_multiline_state(self, _):
            process = self.process
            is_multiline = self.is_multiline
            self.reset()
            for line in self.default_buffer.text.splitlines():
                process(line)
                self.multiline_state = multiline_state = is_multiline()
                if not multiline_state:
                    return

except ImportError:
    PysPromptToolkitLineShell = PysClassicLineShell