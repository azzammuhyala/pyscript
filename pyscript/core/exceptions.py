from .bases import Pys
from .utils import space_indent

class PysException(Pys):

    def __init__(self, exception, context, position):
        self.exception = exception
        self.context = context
        self.position = position

    def __str__(self):
        return str(self.exception)

    def __repr__(self):
        return '<Exception of {!r}>'.format(self.exception)

    def string_traceback(self):
        context = self.context
        position = self.position

        frames = []

        while context:
            is_positionless = position.is_positionless()

            frames.append(
                '  File "{}"{}{}{}'.format(
                    position.file.name,
                    '' if is_positionless else ', line {}'.format(position.start_line),
                    '' if context.name is None else ', in {}'.format(context.name),
                    '' if is_positionless else '\n{}'.format(space_indent(position.format_arrow(), 4))
                )
            )

            position = context.parent_entry_position
            context = context.parent

        found_duplicated_frame = 0
        strings_traceback = ''
        last_frame = ''

        for frame in reversed(frames):
            if frame == last_frame:
                found_duplicated_frame += 1

            else:
                if found_duplicated_frame > 0:
                    strings_traceback += '  [Previous line repeated {} more times]\n'.format(found_duplicated_frame)
                    found_duplicated_frame = 0

                strings_traceback += frame + '\n'
                last_frame = frame

        if found_duplicated_frame > 0:
            strings_traceback += '  [Previous line repeated {} more times]\n'.format(found_duplicated_frame)

        result = 'Traceback (most recent call last):\n' + strings_traceback

        if isinstance(self.exception, type):
            return result + self.exception.__name__

        message = str(self.exception)
        return result + type(self.exception).__name__ + (': ' + message if message else '')

class PysShouldReturn(Pys, BaseException):

    def __init__(self, result):
        super().__init__()
        self.result = result

    def __str__(self):
        if self.result.error is None:
            return '<signal>'

        exception = self.result.error.exception

        if isinstance(exception, type):
            return exception.__name__

        message = str(exception)
        return type(exception).__name__ + (': ' + message if message else '')