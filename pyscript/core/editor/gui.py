from .bases import PysEditor
from ..buffer import PysFileBuffer
from ..constants import ICON_PATH
from ..highlight import PYGMENTS, PygmentsPyScriptStyle, PygmentsPyScriptLexer
from ..utils.generic import boundary
from ..version import __version__

try:
    from tkinter import Tk, Scrollbar, Text, Canvas, messagebox
    from tkinter.font import families, Font

    MONO_FALLBACKS = (
        'Fira Code',
        'Cascadia Code', 'SF Mono', 'Ubuntu Mono', 'Liberation Mono',
        'Consolas', 'Menlo', 'DejaVu Sans Mono',
        'Courier New', 'Lucida Console', 'Monaco', 'Andale Mono',
        'Courier', 'Terminal',
        'monospace'
    )

    class PysGUIEditor(PysEditor, Tk):

        def __init__(self, file: PysFileBuffer, colored: bool = True) -> None:
            PysEditor.__init__(self, file, colored)
            Tk.__init__(self)

            def update_tab_size():
                self.text.configure(tabs=(self.font.measure('    '),))

            def on_save(event=None):
                text = self.text.get('1.0', 'end')
                self.save(text[:-1] if text.endswith(('\r\n', '\r', '\n')) else text)
                update()
                return 'break'

            def on_close():
                if self.modified:
                    answer = messagebox.askyesnocancel('Unsaved changes', 'File has been modified. Save before exit?')
                    if answer is None:
                        return
                    elif answer:
                        on_save()
                self.save_configuration()
                self.destroy()

            def on_configure(event):
                if event.widget == self:
                    zoom = self.wm_state() == 'zoomed'
                    self.set_configuration('zoom', zoom)
                    if not zoom:
                        self.set_configuration('gui-geometry', f'{event.width}x{event.height}+{event.x}+{event.y}')

            def on_modified(event=None):
                if self.text.edit_modified():
                    self.modified = True
                    update()
                    refresh_line_numbers()
                    self.text.edit_modified(False)

            def on_change_font(value):
                def wrapper(event=None):
                    font = self.font
                    size = boundary(font.cget('size') + value, 1, 127)
                    font.config(size=size)
                    update_tab_size()
                    refresh_line_numbers()
                    self.set_configuration('gui-size-font', size)
                    return 'break'
                return wrapper

            def on_toggle_wrap(event=None):
                text = self.text
                wrap = text.cget('wrap') != 'char'
                text.configure(wrap='char' if wrap else 'none')
                refresh_line_numbers()
                self.set_configuration('wrap', wrap)
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
                if text.tag_ranges('sel'):
                    text.delete('sel.first', 'sel.last')

                line = text.get('insert linestart', 'insert lineend')
                text.insert('insert', '\n' + line[:len(line) - len(line.lstrip())])
                text.see('insert')
                return 'break'

            def draw_line_numbers():
                self.line_job = None
                text = self.text
                canvas = self.line_numbers
                font = self.font

                bold = (font.cget('family'), font.cget('size'), 'bold')
                digits = len(text.index('end-1c').split('.')[0])
                padding = font.measure(' ')
                width = font.measure('0' * digits) + padding * 2

                canvas.delete('all')
                canvas.configure(width=width, bg='#1f1f1f')

                current = text.index('insert').split('.')[0]
                index = text.index('@0,0')
                previous = None

                while True:
                    info = text.dlineinfo(index)
                    if info is None:
                        break

                    number = index.split('.')[0]
                    if number == previous:
                        break

                    canvas.create_text(
                        width - padding, info[1],
                        anchor='ne',
                        text=number,
                        font=bold if number == current else font,
                        fill='#ffffff'
                    )

                    previous = number
                    index = text.index(f'{index} +1 lines')

            def refresh_line_numbers(event=None):
                if self.line_job is None:
                    self.line_job = self.after_idle(draw_line_numbers)

            def on_scroll(first, last):
                self.scrollbar.set(first, last)
                refresh_line_numbers()

            installed = frozenset(families())
            for font_name in MONO_FALLBACKS:
                if font_name in installed:
                    break
            else:
                font_name = 'monospace'

            self.line_job = None
            self.font = Font(
                family=font_name,
                size=boundary(self.get_configuration('gui-size-font', 10), 1, 127)
            )
            self.scrollbar = Scrollbar(self)
            self.line_numbers = Canvas(
                self,
                width=0,
                highlightthickness=0,
                bd=0
            )
            self.text = Text(
                self,
                undo=True,
                width=120,
                font=self.font,
                wrap='char' if self.get_configuration('wrap', True) else 'none',
                bg='#000000',
                fg='#ffffff',
                insertbackground='white',
                yscrollcommand=on_scroll
            )

            update_tab_size()

            self.scrollbar.pack_configure(side='right', fill='y')
            self.scrollbar.configure(command=self.text.yview)

            self.line_numbers.pack_configure(side='left', fill='y')
            self.text.pack_configure(side='left', expand=True, fill='both')
            self.text.pack_configure(side='left', expand=True, fill='both')

            self.text.insert('1.0', self.file.text)
            self.text.edit_modified(False)

            self.text.bind('<<Modified>>', on_modified)
            self.text.bind('<Return>', on_enter)
            self.text.bind('<Prior>', on_page_up)
            self.text.bind('<Next>', on_page_down)
            self.text.bind('<KeyRelease>', refresh_line_numbers)
            self.text.bind('<ButtonRelease-1>', refresh_line_numbers)
            self.text.bind('<Configure>', refresh_line_numbers)

            self.bind('<Configure>', on_configure)
            self.bind_all('<Control-S>', on_save)
            self.bind_all('<Control-s>', on_save)
            self.bind_all('<Control-W>', on_toggle_wrap)
            self.bind_all('<Control-w>', on_toggle_wrap)
            self.bind_all('<Control-minus>', on_change_font(-1))
            self.bind_all('<Control-underscore>', on_change_font(-5))
            self.bind_all('<Control-equal>', on_change_font(1))
            self.bind_all('<Control-plus>', on_change_font(5))

            try:
                self.wm_iconbitmap(ICON_PATH)
            except:
                pass

            if self.get_configuration('zoom', False):
                self.wm_state('zoomed')

            self.wm_geometry(
                self.get_configuration(
                    'gui-geometry',
                    f'500x500+{self.winfo_screenwidth() // 2 - 250}+{self.winfo_screenheight() // 2 - 250}'
                )
            )

            self.wm_minsize(250, 200)
            self.wm_protocol('WM_DELETE_WINDOW', on_close)

            if PYGMENTS and colored:
                self.lexer = PygmentsPyScriptLexer()
                self.refresh_job = None

                tag_configure = self.text.tag_configure
                for token, style in PygmentsPyScriptStyle.list_styles():
                    color = style['color']
                    if color:
                        tag_configure(str(token), foreground=f'#{color}')

                def refresh_highlight():
                    self.refresh_job = None

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

                def update():
                    self.title(f'PyScript {__version__} - {self.basename}{"*" if self.modified else ""}')
                    if self.refresh_job is not None:
                        self.after_cancel(self.refresh_job)
                    self.refresh_job = self.after(500, refresh_highlight)

            else:
                def update():
                    self.title(f'PyScript {__version__} - {self.basename}{"*" if self.modified else ""}')

            update()
            refresh_line_numbers()

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