from .bases import PysEditor
from ..buffer import PysFileBuffer

try:

    from ..constants import ICON_PATH
    from ..highlight import PygmentsPyScriptStyle, PygmentsPyScriptLexer
    from ..version import __version__

    from tkinter import END, Tk, Scrollbar, Text, messagebox
    from tkinter.font import Font

    class PysGUIEditor(PysEditor, Tk):

        def __init__(self, file: PysFileBuffer) -> None:
            PysEditor.__init__(self, file)
            Tk.__init__(self)

            try:
                self.iconbitmap(ICON_PATH)
            except:
                pass

            self.lexer = PygmentsPyScriptLexer()
            self.style = PygmentsPyScriptStyle

            self.font = Font(family='Consolas', size=10)

            self.scrollbar = Scrollbar(self)
            self.scrollbar.pack_configure(side='right', fill='y')

            self.text = Text(
                self,
                undo=True,
                width=120,
                font=self.font,
                wrap='char',
                bg='#131313',
                fg='#f8f8f2',
                insertbackground='white',
                yscrollcommand=self.scrollbar.set
            )

            self.text.pack_configure(side='left', expand=True, fill='both')
            self.scrollbar.configure(command=self.text.yview)

            self.text.insert('1.0', self.file.text)
            self.text.edit_modified(False)

            self.text.bind('<<Modified>>', self.on_modified)

            self.bind_all('<Control-S>', self.on_save)
            self.bind_all('<Control-s>', self.on_save)
            self.bind_all('<Control-W>', self.on_toggle_wrap)
            self.bind_all('<Control-w>', self.on_toggle_wrap)
            self.bind_all('<Control-minus>', self.on_change_font(-1, lambda size : size > 1))
            self.bind_all('<Control-underscore>', self.on_change_font(-5, lambda size : size > 1))
            self.bind_all('<Control-equal>', self.on_change_font(1, lambda size : size < 128))
            self.bind_all('<Control-plus>', self.on_change_font(5, lambda size : size < 128))

            self.protocol('WM_DELETE_WINDOW', self.on_close)

            self.setup_tags()
            self.update()

        def setup_tags(self):
            tag_configure = self.text.tag_configure
            for token, style in self.style.list_styles():
                if color := style['color']:
                    tag_configure(str(token), foreground=f'#{color}')

        def update(self):
            self.title(f'PyScript {__version__} - {self.basename}{"*" if self.modified else ""}')

            index = '1.0'

            text = self.text
            text_tag_add = text.tag_add
            text_tag_remove = text.tag_remove
            text_index = text.index

            for tag in text.tag_names():
                if tag != 'sel':
                    text_tag_remove(tag, '1.0', END)

            for type, value in self.lexer.get_tokens(text.get('1.0', END)):
                end_index = text_index(f'{index} + {len(value)} chars')
                text_tag_add(str(type), index, end_index)
                index = end_index

        def on_save(self, event=None):
            self.save(self.text.get('1.0', END))
            self.update()
            return 'break'

        def on_close(self):
            if self.modified:
                answer = messagebox.askyesnocancel('Unsaved changes', 'File has been modified. Save before exit?')
                if answer is True:
                    self.on_save()
                    self.destroy()
                elif answer is False:
                    self.destroy()
            else:
                self.destroy()

        def on_modified(self, event=None):
            text = self.text
            if text.edit_modified():
                self.modified = True
                self.update()
                text.edit_modified(False)

        def on_change_font(self, value, limit):
            def wrapper(event=None):
                font = self.font
                size = font.cget('size')
                if limit(size):
                    font.config(size=size + value)
                return 'break'
            return wrapper

        def on_toggle_wrap(self, event=None):
            self.wrapped = not self.wrapped
            self.text.configure(wrap='char' if self.wrapped else 'none')
            return 'break'

        def run(self):
            PysEditor.run(self)
            Tk.mainloop(self)

except ImportError as e:
    _error = e

    class PysGUIEditor(PysEditor):
        def __new__(cls, *args, **kwargs):
            raise ImportError(
                "cannot import module tkinter. Did you forgot install separate tkinter module or "
                "not check the option for tkinter during python installation?: " +
                str(_error)
            ) from _error