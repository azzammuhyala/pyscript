from .bases import Pys
from .buffer import PysFileBuffer
from .constants import ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE
from .mapping import GET_ACOLOR
from .utils.decorators import typecheck, immutable
from .utils.generic import setimuattr, save_get_environ

MAXIMUM_TRACEBACK_LINE = save_get_environ(ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE, '5')
try:
    MAXIMUM_TRACEBACK_LINE = max(3, int(MAXIMUM_TRACEBACK_LINE))
except:
    MAXIMUM_TRACEBACK_LINE = 5

@immutable
class PysPosition(Pys):

    __slots__ = ('file', 'start', 'end', 'start_line', 'start_column', 'end_line', 'end_column', 'is_positionless')

    @typecheck
    def __init__(self, file: PysFileBuffer, start: int, end: int) -> None:
        is_positionless = start < 0 or end < 0 or start > end or end > len(file.text) + 1

        if is_positionless:
            start = -1
            end = -1
            start_line = -1
            start_column = -1
            end_line = -1
            end_column = -1
        else:
            text_count = file.text.count
            text_rfind = file.text.rfind
            start_line = text_count('\n', 0, start) + 1
            start_column = start - text_rfind('\n', 0, start)
            end_line = text_count('\n', 0, end) + 1
            end_column = end - text_rfind('\n', 0, end)

        setimuattr(self, 'file', file)
        setimuattr(self, 'is_positionless', is_positionless)
        setimuattr(self, 'start', start)
        setimuattr(self, 'end', end)
        setimuattr(self, 'start_line', start_line)
        setimuattr(self, 'start_column', start_column)
        setimuattr(self, 'end_line', end_line)
        setimuattr(self, 'end_column', end_column)

    def __repr__(self) -> str:
        return f'<Position({self.start!r}, {self.end!r}) from {self.file.name!r}>'

    def format_error_arrow(self, colored: bool = True) -> str:
        if self.is_positionless:
            return ''

        if colored:
            reset = GET_ACOLOR('reset')
            bred =  GET_ACOLOR('bold-red')
        else:
            reset = ''
            bred = ''

        text = self.file.text

        start = text.rfind('\n', 0, self.start) + 1
        end = text.find('\n', start + 1)
        if end == -1:
            end = len(text)

        if text[self.start:self.end] in ('', '\n'):
            if self.start > start:
                line = text[start:end].lstrip().replace('\t', ' ').replace('\v', ' ')
                return f'{line}\n{bred}{" " * len(line)}^{reset}'
            return f'\n{bred}^{reset}'

        column_start = self.start_column
        column_end = self.end_column
        count = self.end_line - self.start_line + 1
        reach_maximum_line = count > MAXIMUM_TRACEBACK_LINE
        range_line = {0, count - 1}
        lines = []

        for i in range(count):
            line = text[start:end].lstrip('\n')

            if not reach_maximum_line or i in range_line:
                lines.append((
                    line, len(line.lstrip()),
                    column_start - 1 if i == 0 else 0,
                    column_end - 1 if i == count - 1 else len(line)
                ))

            start = end
            end = text.find('\n', start + 1)
            if end == -1:
                end = len(text)

        minimum_indent = min(len(line) - code_length for line, code_length, _, _ in lines)
        result = []

        for i, (line, code_length, start, end) in enumerate(lines):
            line = line[minimum_indent:]
            end_index = end - minimum_indent

            if i == 0:
                start_index = start - minimum_indent
                arrow = '^' * (end - start)
                line = f'{line[:start_index]}{bred}{line[start_index:end_index]}{reset}{line[end_index:]}\n' \
                    f'{" " * start_index}{bred}{arrow}{reset}'

            else:
                indent = len(line) - code_length
                arrow = '^' * (end - start - (minimum_indent + indent))
                line = f'{line[:indent]}{bred}{line[indent:end_index]}{reset}{line[end_index:]}\n' \
                    f'{" " * indent}{bred}{arrow}{reset}'

                if reach_maximum_line and i == 1:
                    result.append(f'...<{count - 2} lines>...')

            result.append(line)

        return '\n'.join(result).replace('\t', ' ').replace('\v', ' ')