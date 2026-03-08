from .bases import PysEditor
from ..buffer import PysFileBuffer
from ..constants import ICON_PATH
from ..highlight import PygmentsPyScriptStyle, PygmentsPyScriptLexer
from ..version import __version__

try:
    from tkinter import Tk, Scrollbar, Text, messagebox
    from tkinter.font import Font

    class PysGUIEditor(PysEditor, Tk):

        def __init__(self, file: PysFileBuffer) -> None:
            PysEditor.__init__(self, file)
            Tk.__init__(self)

            def setup_tags():
                tag_configure = self.text.tag_configure
                for token, style in PygmentsPyScriptStyle.list_styles():
                    if color := style['color']:
                        tag_configure(str(token), foreground=f'#{color}')

            def update():
                self.title(f'PyScript {__version__} - {self.basename}{"*" if self.modified else ""}')

                index = '1.0'

                text = self.text
                text_tag_add = text.tag_add
                text_tag_remove = text.tag_remove
                text_index = text.index
                get_length = len
                to_string = str

                for tag in text.tag_names():
                    if tag != 'sel':
                        text_tag_remove(tag, '1.0', 'end')

                for type, value in self.lexer.get_tokens(text.get('1.0', 'end')):
                    end_index = text_index(f'{index} + {get_length(value)} chars')
                    text_tag_add(to_string(type), index, end_index)
                    index = end_index

            def on_save(event=None):
                self.save(self.text.get('1.0', 'end'))
                update()
                return 'break'

            def on_close():
                if self.modified:
                    answer = messagebox.askyesnocancel('Unsaved changes', 'File has been modified. Save before exit?')
                    if answer is True:
                        on_save()
                        self.destroy()
                    elif answer is False:
                        self.destroy()
                else:
                    self.destroy()

            def on_modified(event=None):
                text = self.text
                if text.edit_modified():
                    self.modified = True
                    update()
                    text.edit_modified(False)

            def on_change_font(value, limit):
                def wrapper(event=None):
                    font = self.font
                    size = font.cget('size')
                    if limit(size):
                        font.config(size=size + value)
                    return 'break'
                return wrapper

            def on_toggle_wrap(event=None):
                self.wrapped = not self.wrapped
                self.text.configure(wrap='char' if self.wrapped else 'none')
                return 'break'

            def on_page_up(event=None):
                text = self.text
                text.mark_set('insert', '1.0')
                text.see('insert')
                return 'break'

            def on_page_down(event=None):
                text = self.text
                text.mark_set('insert', 'end')
                text.see('insert')
                return 'break'

            def on_enter(event=None):
                text = self.text
                line = text.get('insert linestart', 'insert lineend')
                text.insert('insert', '\n' + line[:len(line) - len(line.lstrip())])
                return 'break'

            try:
                self.wm_iconbitmap(ICON_PATH)
            except:
                pass

            self.lexer = PygmentsPyScriptLexer()
            self.font = Font(family='Consolas', size=10)
            self.scrollbar = Scrollbar(self)
            self.text = Text(
                self,
                undo=True,
                width=120,
                font=self.font,
                wrap='char',
                bg='#171717',
                fg='#f1f1f1',
                insertbackground='white',
                yscrollcommand=self.scrollbar.set
            )

            self.text.pack_configure(side='left', expand=True, fill='both')

            self.text.insert('1.0', self.file.text)
            self.text.edit_modified(False)

            self.text.bind('<<Modified>>', on_modified)
            self.text.bind('<Return>', on_enter)
            self.text.bind('<Prior>', on_page_up)
            self.text.bind('<Next>', on_page_down)

            self.scrollbar.pack_configure(side='right', fill='y')
            self.scrollbar.configure(command=self.text.yview)

            self.bind_all('<Control-S>', on_save)
            self.bind_all('<Control-s>', on_save)
            self.bind_all('<Control-W>', on_toggle_wrap)
            self.bind_all('<Control-w>', on_toggle_wrap)
            self.bind_all('<Control-minus>', on_change_font(-1, lambda size : size > 1))
            self.bind_all('<Control-underscore>', on_change_font(-5, lambda size : size > 1))
            self.bind_all('<Control-equal>', on_change_font(1, lambda size : size < 128))
            self.bind_all('<Control-plus>', on_change_font(5, lambda size : size < 128))

            self.wm_protocol('WM_DELETE_WINDOW', on_close)

            setup_tags()
            update()

        def run(self) -> None:
            PysEditor.run(self)
            Tk.mainloop(self)

    GUI_SUPPORT = True

except BaseException as e:
    _error = e

    class PysGUIEditor(PysEditor):
        def __new__(cls, *args, **kwargs):
            raise ImportError(
                "cannot import module tkinter. Did you forgot install separate tkinter module or "
                f"not check the option for tkinter during python installation?: {_error}"
            ) from _error

    GUI_SUPPORT = False