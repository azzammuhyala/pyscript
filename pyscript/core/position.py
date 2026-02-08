from .bases import Pys
from .buffer import PysFileBuffer
from .constants import ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE
from .mapping import ACOLORS
from .utils.decorators import typechecked, immutable
from .utils.generic import setimuattr

from os import environ

MAXIMUM_TRACEBACK_LINE = environ.get(ENV_PYSCRIPT_MAXIMUM_TRACEBACK_LINE)
if MAXIMUM_TRACEBACK_LINE is None:
    MAXIMUM_TRACEBACK_LINE = 5
else:
    try:
        MAXIMUM_TRACEBACK_LINE = max(3, int(MAXIMUM_TRACEBACK_LINE))
    except:
        MAXIMUM_TRACEBACK_LINE = 5

@immutable
class PysPosition(Pys):

    __slots__ = ('file', 'start', 'end', 'start_line', 'start_column', 'end_line', 'end_column', 'is_positionless')

    @typechecked
    def __init__(self, file: PysFileBuffer, start: int, end: int) -> None:
        is_positionless = start < 0 or end < 0 or start > end or end > len(file.text) + 1

        setimuattr(self, 'file', file)
        setimuattr(self, 'start', -1 if is_positionless else start)
        setimuattr(self, 'end', -1 if is_positionless else end)
        setimuattr(self, 'start_line', -1 if is_positionless else file.text.count('\n', 0, start) + 1)
        setimuattr(self, 'start_column', -1 if is_positionless else start - file.text.rfind('\n', 0, start))
        setimuattr(self, 'end_line', -1 if is_positionless else file.text.count('\n', 0, end) + 1)
        setimuattr(self, 'end_column', -1 if is_positionless else end - file.text.rfind('\n', 0, end))
        setimuattr(self, 'is_positionless', is_positionless)

    def __repr__(self) -> str:
        return f'<Position({self.start!r}, {self.end!r}) from {self.file.name!r}>'

def format_error_arrow(position, colored=True):
    if position.is_positionless:
        return ''

    if colored:
        reset = ACOLORS('reset')
        bred =  ACOLORS('bold-red')
    else:
        reset = ''
        bred = ''

    text = position.file.text
    line_start = position.start_line
    line_end = position.end_line
    column_start = position.start_column
    column_end = position.end_column

    start = text.rfind('\n', 0, position.start) + 1
    end = text.find('\n', start + 1)
    if end == -1:
        end = len(text)

    if text[position.start:position.end] in ('', '\n'):
        if position.start > start:
            line = text[start:end].lstrip().replace('\t', ' ')
            return f'{line}\n{bred}{" " * len(line)}^{reset}'
        return f'\n{bred}^{reset}'

    result = []
    lines = []
    count = line_end - line_start + 1
    reach_maximum_line = count > MAXIMUM_TRACEBACK_LINE
    range_line = {0, count - 1}

    for i in range(count):
        line = text[start:end].lstrip('\n')

        if not reach_maximum_line or i in range_line:
            lines.append(
                (
                    line, len(line.lstrip()),
                    column_start - 1 if i == 0 else 0,
                    column_end - 1 if i == count - 1 else len(line)
                )
            )

        start = end
        end = text.find('\n', start + 1)
        if end == -1:
            end = len(text)

    minimum_indent = min(len(line) - code_length for line, code_length, _, _ in lines)

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
                result.append(f'{" " * indent}...<{count - 2} lines>...')

        if arrow:
            result.append(line)

    return '\n'.join(result).replace('\t', ' ')