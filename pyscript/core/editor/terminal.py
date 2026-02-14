from .bases import PysEditor
from ..buffer import PysFileBuffer
from ..highlight import PygmentsPyScriptStyle, PygmentsPyScriptLexer
from ..version import __version__

try:
    from prompt_toolkit.application import Application
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import Layout, HSplit, Window, Float, FloatContainer
    from prompt_toolkit.layout.containers import ConditionalContainer
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.layout.processors import TabsProcessor
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.styles.pygments import style_from_pygments_cls
    from prompt_toolkit.widgets import TextArea

    class PysTerminalEditor(PysEditor, Application):

        def __init__(self, file: PysFileBuffer) -> None:
            PysEditor.__init__(self, file)

            self.show_exit_window = False

            on_edit = Condition(lambda: not self.show_exit_window)
            on_exit = Condition(lambda: self.show_exit_window)
            on_wrap = Condition(lambda: self.wrapped)

            self.text = TextArea(
                multiline=True,
                scrollbar=True,
                wrap_lines=on_wrap,
                lexer=PygmentsLexer(PygmentsPyScriptLexer),
                input_processors=[
                    TabsProcessor(tabstop=4)
                ]
            )

            self.title = Window(
                content=FormattedTextControl(self.create_title),
                height=1
            )

            self.close_window = Window(
                content=FormattedTextControl("File has been modified. Save before exit?\n(Y)es / (N)o / (C)ancel"),
                height=2,
                style='reverse'
            )

            self.exit_container = ConditionalContainer(
                content=self.close_window,
                filter=on_exit,
            )

            self.key_bindings = KeyBindings()

            @self.key_bindings.add('tab', filter=on_edit, eager=True)
            def _(event):
                self.text.buffer.insert_text('\t')

            @self.key_bindings.add('c-w', filter=on_edit, eager=True)
            def _(event):
                self.wrapped = not self.wrapped

            @self.key_bindings.add('c-z', filter=on_edit, eager=True)
            def _(event):
                self.current_buffer.undo()

            @self.key_bindings.add('c-s', filter=on_edit, eager=True)
            def _(event):
                self.save(self.text.text)

            @self.key_bindings.add('c-x', filter=on_edit, eager=True)
            @self.key_bindings.add('escape', filter=on_edit, eager=True)
            def _(event):
                if self.modified:
                    self.show_exit_window = True
                    self.layout.focus(self.close_window)
                else:
                    self.exit()

            @self.key_bindings.add('y', filter=on_exit)
            def _(event):
                self.save(self.text.text)
                self.show_exit_window = False
                self.exit()

            @self.key_bindings.add('n', filter=on_exit)
            def _(event):
                self.show_exit_window = False
                self.exit()

            @self.key_bindings.add('c', filter=on_exit)
            def _(event):
                self.show_exit_window = False
                self.layout.focus(self.text)

            self.root = FloatContainer(
                content=HSplit(
                    [
                        self.title,
                        self.text,
                    ]
                ),
                floats=[
                    Float(
                        content=self.exit_container,
                        left=2,
                        bottom=1
                    )
                ]
            )

            self.text.text = self.file.text
            self.text.buffer.on_text_changed += self.on_change

            Application.__init__(
                self,
                layout=Layout(self.root),
                style=style_from_pygments_cls(PygmentsPyScriptStyle),
                key_bindings=self.key_bindings,
                full_screen=True,
                mouse_support=True,
                paste_mode=True
            )

        def run(self) -> None:
            PysEditor.run(self)
            Application.run(self)

        def on_change(self, buffer):
            self.modified = True

        def create_title(self):
            columns = self.output.get_size().columns
            file = f'{self.basename}{"*" if self.modified else ""}'
            title = f'  PyScript {__version__} - {file}  '
            if len(title) > columns:
                title = file
            return ANSI(f'\x1b[7m{title}{" " * max(0, columns - len(title))}\x1b[0m')

    TERMINAL_SUPPORT = True

except ImportError as e:
    _error = e

    class PysTerminalEditor(PysEditor):
        def __new__(cls, *args, **kwargs):
            raise ImportError(f"cannot import module prompt_toolkit: {_error}") from _error

    TERMINAL_SUPPORT = False