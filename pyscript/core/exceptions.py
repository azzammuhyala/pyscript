from .bases import Pys
from .utils import get_line_column_by_index, format_highlighted_text_with_arrow

class PysException(Pys):

    def __init__(self, exception, position, context):
        self.exception = exception
        self.position = position
        self.context = context

    def __str__(self):
        return str(self.exception)

    def __repr__(self):
        return "<PysException of {!r}>".format(self.exception)

    def generate_string_traceback(self):
        strings_traceback = ''

        context = self.context
        file = context.file
        position = self.position

        while context:
            line_start, _ = get_line_column_by_index(position.start, file)
            last_strings_traceback = strings_traceback
            strings_traceback = '  File "{}", line {}'.format(file.name, line_start)

            if context.name is not None:
                strings_traceback += ', in {}'.format(context.name)

            strings_traceback += '\n    '
            strings_traceback += '\n    '.join(format_highlighted_text_with_arrow(position, file).splitlines()) + '\n'
            strings_traceback += last_strings_traceback

            file = context.file
            position = context.parent_entry_position
            context = context.parent

        if isinstance(self.exception, type):
            name = self.exception.__name__
            message = ''
        else:
            name = type(self.exception).__name__
            message = str(self.exception)

        result = 'Traceback (most recent call last):\n{}{}'.format(strings_traceback, name)
        if message:
            result += ': {}'.format(message)

        return result