from .bases import Pys
from .cache import pys_sys
from .constants import GLOBAL_HISTORY_PATH, ENV_PYSCRIPT_HISTORY_PATH, ENV_PYSCRIPT_MAXIMUM_HISTORY_LINE
from .exceptions import PysSignal
from .mapping import BRACKETS_MAP
from .utils.debug import print_traceback
from .utils.decorators import singleton
from .utils.path import normpath

from typing import Iterable, Literal, Optional

import os
import sys

class PysIncompleteHandler(Pys):

    def __init__(self) -> None:
        self._brackets_stack = []
        self.reset()

    def reset(self) -> None:
        self._brackets_stack.clear()
        self._in_string = False
        self._in_decorator = False
        self._is_triple_string = False
        self._line_continuation = False
        self._must_break = False
        self._string_prefix = ''
        self.text = ''

    def _is_multiline(self) -> bool:
        return not self._must_break and (
            len(self._brackets_stack) > 0 or
            self._line_continuation or
            self._is_triple_string or
            self._in_decorator
        )

    def _process_line(self, text: str) -> None:
        self._in_decorator = False
        self._line_continuation = False

        is_space = True
        index = 0

        while index < len(text):
            character = text[index]

            if character == '\\':
                index += 1
                character = text[index:index+1]

                if character == '':
                    self._line_continuation = True
                    break
                elif not self._in_string:
                    self._must_break = True
                    break

            elif character in '\'"':
                bind_3 = text[index:index+3]

                if self._is_triple_string:
                    if self._string_prefix * 3 == bind_3:
                        self._in_string = False
                        self._is_triple_string = False
                        index += 2

                else:
                    if not self._in_string and bind_3 in ("'''", '"""'):
                        self._is_triple_string = True
                        index += 2

                    if self._in_string:
                        if self._string_prefix == character:
                            self._in_string = False
                    else:
                        self._string_prefix = character
                        self._in_string = True

            if not self._in_string:

                if character == '#':
                    break

                elif character == '$':
                    index += 1
                    while index < len(text) and (character := text[index]).isspace():
                        index += 1
                    if not character.isidentifier():
                        self._must_break = True
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
                    if self._must_break:
                        break

                elif character == '`':
                    self._must_break = True
                    break

                if is_space and not character.isspace():
                    is_space = False

            index += 1

        if self._in_decorator and is_space:
            self._in_decorator = False
        if self._in_string and not (self._line_continuation or self._is_triple_string):
            self._must_break = True

        if self._is_multiline():
            self.text += text + '\n'
        else:
            self.text += text

class PysLineShell(PysIncompleteHandler):

    def __init__(self, ps1: str = '>>> ', ps2: str = '... ', colored: bool = True) -> None:
        super().__init__()
        self._colored = colored
        self.ps1 = ps1
        self.ps2 = ps2

    @property
    def colored(self):
        return self._colored

    def _process_command(self, text: str) -> Literal[-1, 0, 1] | None:
        if text == '/exit':
            return 0

        elif text == '/clean':
            return 1

        elif text == '/clear':
            try:
                pys_sys.clearhook()
            except:
                try:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    print('An exception occurred while calling clearhook function:', file=sys.stderr)
                    if exc_type is PysSignal and (exc_tb := exc_value.result.error) is not None:
                        print_traceback(None, None, exc_tb)
                    else:
                        sys.excepthook(exc_type, exc_value, exc_tb)
                except:
                    pass
            return -1

    def prompt(self) -> Literal[0]:
        return 0

class PysClassicLineShell(PysLineShell):

    def prompt(self) -> str | Literal[0, 1]:
        reset = self.reset
        is_multiline = self._is_multiline
        process_line = self._process_line
        process_command = self._process_command

        multiline = False
        reset()

        while True:

            try:

                if multiline:
                    text = input(self.ps2)
                else:
                    text = input(self.ps1)
                    code = process_command(text)
                    if code is not None:
                        if code == -1:
                            continue
                        return code

            except (OSError, ValueError):
                return 0

            except (MemoryError, UnicodeDecodeError):
                print("InputError", file=sys.stderr)
                continue

            process_line(text)

            if is_multiline():
                multiline = True
            else:
                text = self.text
                reset()
                return text

try:
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.history import History, InMemoryHistory
    from prompt_toolkit.layout.processors import TabsProcessor
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.output.color_depth import ColorDepth
    from prompt_toolkit.shortcuts.prompt import PromptSession
    from prompt_toolkit.styles.pygments import style_from_pygments_cls

    HISTORY_PATH = os.environ.get(ENV_PYSCRIPT_HISTORY_PATH, GLOBAL_HISTORY_PATH)
    if HISTORY_PATH and HISTORY_PATH != '<none>':
        HISTORY_PATH = normpath(HISTORY_PATH)
        USE_FILE_HISTORY = True
    else:
        HISTORY_PATH = '<none>'
        USE_FILE_HISTORY = False

    MAXIMUM_HISTORY_LINE = os.environ.get(ENV_PYSCRIPT_MAXIMUM_HISTORY_LINE)
    if MAXIMUM_HISTORY_LINE is None:
        MAXIMUM_HISTORY_LINE = 1000
    else:
        try:
            MAXIMUM_HISTORY_LINE = int(MAXIMUM_HISTORY_LINE)
        except:
            MAXIMUM_HISTORY_LINE = 1000

    @singleton
    class PysHistory(Pys, History):

        def __new_singleton__(cls) -> 'PysHistory':
            if USE_FILE_HISTORY:
                return super().__new__(cls)
            raise NotImplementedError('not using file history')

        def update_history(self, append_string: Optional[str] = None) -> list[str]:
            try:

                if MAXIMUM_HISTORY_LINE == 0:
                    with open(HISTORY_PATH, 'w', encoding='utf-8') as file:
                        file.write('')
                    return []

                strings = []
                lines = []
                update_history = False

                if os.path.isfile(HISTORY_PATH):

                    def add_to_string():
                        strings.append('\n'.join(lines))
                        lines.clear()

                    with open(HISTORY_PATH, 'r', encoding='utf-8') as file:

                        for line in file:
                            line = line[:-1]
                            if line.startswith('\x1e'):
                                add_to_string()
                                line = line[1:]
                            lines.append(line)

                        if lines:
                            add_to_string()

                else:
                    update_history = True

                if append_string is not None:
                    strings.append(append_string)
                    update_history = True

                if MAXIMUM_HISTORY_LINE > 0 and len(strings) > MAXIMUM_HISTORY_LINE:
                    del strings[:-MAXIMUM_HISTORY_LINE]
                    update_history = True

                if update_history:
                    with open(HISTORY_PATH, 'w', encoding='utf-8') as file:
                        file.writelines(f'\x1e{line}\n' for line in strings)

                return strings

            except:
                return []

        def load_history_strings(self) -> Iterable[str]:
            return reversed(self.update_history())

        def store_string(self, string: str) -> None:
            self.update_history(string)

        def append_string(self, string: str) -> None:
            if MAXIMUM_HISTORY_LINE == 0:
                self._loaded_strings.clear()
                self.update_history()
                return

            elif MAXIMUM_HISTORY_LINE > 0:
                length = len(self._loaded_strings)
                if length == MAXIMUM_HISTORY_LINE:
                    del self._loaded_strings[-1]
                elif length > MAXIMUM_HISTORY_LINE:
                    del self._loaded_strings[:-MAXIMUM_HISTORY_LINE]

            self._loaded_strings.insert(0, string)
            self.update_history(string)

    history = (PysHistory if USE_FILE_HISTORY else InMemoryHistory)()

    class PysPromptToolkitLineShell(PysLineShell, PromptSession):

        def __init__(self, ps1: str = '>>> ', ps2: str = '... ', colored: bool = True) -> None:
            PysLineShell.__init__(self, ps1, ps2, colored)

            key_bindings = KeyBindings()

            def newline_with_indent():
                buffer = self.default_buffer
                line = buffer.document.current_line_before_cursor
                buffer.insert_text('\n' + line[:len(line) - len(line.lstrip())])

            @key_bindings.add('tab', eager=True)
            def _(event):
                self.default_buffer.insert_text('\t')

            @key_bindings.add('c-n', eager=True)
            def _(event):
                self.default_buffer.insert_text('\n')

            @key_bindings.add('s-tab', eager=True)
            def _(event):
                newline_with_indent()

            @key_bindings.add('pageup', eager=True)
            def _(event):
                self.default_buffer.cursor_position = 0

            @key_bindings.add('pagedown', eager=True)
            def _(event):
                buffer = self.default_buffer
                buffer.cursor_position = len(buffer.text)

            @key_bindings.add('enter', eager=True)
            def _(event):
                buffer = self.default_buffer
                document = buffer.document
                reset = self.reset
                is_multiline = self._is_multiline
                process_line = self._process_line

                reset()

                # Ctrl + Z
                if document.current_line_before_cursor.startswith('\x1a'):
                    self.app.exit(exception=EOFError)
                    return

                row = document.cursor_position_row
                should_process_lines = True

                for i, line in enumerate((buffer.text + '\n').splitlines()):
                    process_line(line)
                    if self._must_break:
                        reset()
                        buffer.validate_and_handle()
                        return
                    if i == row and is_multiline():
                        should_process_lines = False

                if should_process_lines and not is_multiline():
                    reset()
                    buffer.validate_and_handle()
                    return

                newline_with_indent()

            other_keyword = {}

            if colored:
                # circular import problem solved
                from .highlight import PYGMENTS, PygmentsPyScriptStyle, PygmentsPyScriptShellLexer

                if PYGMENTS:
                    other_keyword.update({
                        'lexer': PygmentsLexer(PygmentsPyScriptShellLexer),
                        'style': style_from_pygments_cls(PygmentsPyScriptStyle)
                    })

            else:
                other_keyword.update({
                    'color_depth': ColorDepth.DEPTH_1_BIT
                })

            PromptSession.__init__(
                self,
                input_processors=[TabsProcessor(tabstop=4)],
                key_bindings=key_bindings,
                prompt_continuation=lambda width, line_number, is_soft_wrap: self._ps2,
                history=history,
                **other_keyword
            )

        def prompt(self) -> str | Literal[0, 1]:
            prompt = PromptSession.prompt
            process_command = self._process_command

            self.reset()

            while True:

                try:
                    text = prompt(self, self._ps1)

                    if '\n' not in text:
                        code = process_command(text)
                        if code is not None:
                            if code == -1:
                                continue
                            return code

                    return text

                except (OSError, ValueError):
                    return 0

                except (MemoryError, UnicodeDecodeError):
                    print("InputError", file=sys.stderr)
                    continue

        @property
        def ps1(self) -> str:
            return self._ps1.value if self._colored else self._ps1

        @ps1.setter
        def ps1(self, value: str) -> None:
            self._ps1 = ANSI(value) if self._colored else value

        @property
        def ps2(self) -> str:
            return self._ps2.value if self._colored else self._ps2

        @ps2.setter
        def ps2(self, value: str) -> None:
            self._ps2 = ANSI(value) if self._colored else value

    ADVANCE_LINE_SHELL_SUPPORT = True

except BaseException as e:
    _error = e

    class PysPromptToolkitLineShell(PysLineShell):
        def __new__(cls, *args, **kwargs):
            raise ImportError(f"cannot import module prompt_toolkit: {_error}") from _error

    ADVANCE_LINE_SHELL_SUPPORT = False