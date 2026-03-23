from .bases import PysEditor
from ..buffer import PysFileBuffer
from ..highlight import PYGMENTS, PygmentsPyScriptStyle, PygmentsPyScriptLexer
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
    from prompt_toolkit.output.color_depth import ColorDepth
    from prompt_toolkit.styles.pygments import style_from_pygments_cls
    from prompt_toolkit.widgets import TextArea

    class PysTerminalEditor(PysEditor, Application):

        def __init__(self, file: PysFileBuffer, colored: bool = True) -> None:
            PysEditor.__init__(self, file, colored)

            self.show_exit_window = False

            on_edit = Condition(lambda: not self.show_exit_window)
            on_exit = Condition(lambda: self.show_exit_window)
            on_wrap = Condition(lambda: self.wrapped)

            def on_change(buffer):
                self.modified = True

            text_other_keyword = {}
            close_window_keyword = {}
            app_other_keyword = {}

            if colored:

                if PYGMENTS:
                    text_other_keyword.update({
                        'lexer': PygmentsLexer(PygmentsPyScriptLexer),
                    })
                    app_other_keyword.update({
                        'style': style_from_pygments_cls(PygmentsPyScriptStyle)
                    })

                close_window_keyword.update({
                    'content': FormattedTextControl(
                        " File has been modified. Save before exit? \n"
                        "          (Y)es / (N)o / (C)ancel          "
                    ),
                    'height': 2,
                    'style': 'reverse'
                })

                def create_title():
                    columns = self.output.get_size().columns
                    file = self.basename + ('*' if self.modified else '')
                    title = f'  PyScript {__version__} - {file}  '
                    if len(title) > columns:
                        title = file
                    return ANSI(f'\x1b[7m{title}{" " * max(0, columns - len(title))}\x1b[0m')

            else:
                app_other_keyword.update({
                    'color_depth': ColorDepth.DEPTH_1_BIT
                })
                close_window_keyword.update({
                    'content': FormattedTextControl(
                        "[File has been modified. Save before exit?]\n"
                        "[         (Y)es / (N)o / (C)ancel         ]"
                    ),
                    'height': 2
                })

                def create_title():
                    columns = self.output.get_size().columns
                    file = self.basename + ('*' if self.modified else '')
                    title = f' [PyScript {__version__} - {file}] '
                    if len(title) > columns:
                        title = file
                    return title + ' ' * max(0, columns - len(title))

            self.text = TextArea(
                multiline=True,
                scrollbar=True,
                wrap_lines=on_wrap,
                input_processors=[TabsProcessor(tabstop=4)],
                **text_other_keyword
            )

            self.title = Window(
                content=FormattedTextControl(create_title),
                height=1
            )

            self.close_window = Window(**close_window_keyword)

            self.exit_container = ConditionalContainer(
                content=self.close_window,
                filter=on_exit,
            )

            key_bindings = KeyBindings()

            @key_bindings.add('tab', filter=on_edit, eager=True)
            def _(event):
                self.text.buffer.insert_text('\t')

            @key_bindings.add('pageup', filter=on_edit, eager=True)
            def _(event):
                self.text.buffer.cursor_position = 0

            @key_bindings.add('pagedown', filter=on_edit, eager=True)
            def _(event):
                buffer = self.text.buffer
                buffer.cursor_position = len(buffer.text)

            @key_bindings.add('enter', filter=on_edit, eager=True)
            def _(event):
                buffer = self.text.buffer
                line = buffer.document.current_line_before_cursor
                buffer.insert_text('\n' + line[:len(line) - len(line.lstrip())])

            @key_bindings.add('c-w', filter=on_edit, eager=True)
            def _(event):
                self.wrapped = not self.wrapped

            @key_bindings.add('c-y', filter=on_edit, eager=True)
            def _(event):
                self.text.buffer.redo()

            @key_bindings.add('c-z', filter=on_edit, eager=True)
            def _(event):
                self.text.buffer.undo()

            @key_bindings.add('c-s', filter=on_edit, eager=True)
            def _(event):
                self.save(self.text.buffer.text)

            @key_bindings.add('c-x', filter=on_edit, eager=True)
            @key_bindings.add('escape', filter=on_edit, eager=True)
            def _(event):
                if self.modified:
                    self.show_exit_window = True
                    self.output.hide_cursor()
                    self.layout.focus(self.close_window)
                else:
                    self.exit()

            @key_bindings.add('y', filter=on_exit)
            def _(event):
                self.save(self.text.buffer.text)
                self.show_exit_window = False
                self.exit()

            @key_bindings.add('n', filter=on_exit)
            def _(event):
                self.show_exit_window = False
                self.exit()

            @key_bindings.add('c', filter=on_exit)
            def _(event):
                self.show_exit_window = False
                self.output.show_cursor()
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
            self.text.buffer.on_text_changed += on_change

            Application.__init__(
                self,
                layout=Layout(self.root),
                key_bindings=key_bindings,
                full_screen=True,
                mouse_support=True,
                paste_mode=True,
                **app_other_keyword
            )

        def run(self) -> None:
            PysEditor.run(self)
            Application.run(self)

    TERMINAL_SUPPORT = True

except BaseException as e:
    _error = e

    class PysTerminalEditor(PysEditor):
        def __new__(cls, *args, **kwargs):
            raise ImportError(f"cannot import module prompt_toolkit: {_error}") from _error

    TERMINAL_SUPPORT = False