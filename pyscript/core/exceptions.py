from .bases import Pys
from .constants import NO_COLOR, BOLD
from .utils.decorators import immutable
from .utils.general import setimuattr, space_indent, acolor

@immutable
class PysException(Pys):

    __slots__ = ('exception', 'context', 'position', 'other')

    def __init__(self, exception, context, position, other=None):
        setimuattr(self, 'exception', exception)
        setimuattr(self, 'context', context)
        setimuattr(self, 'position', position)
        setimuattr(self, 'other', other)

    def __repr__(self):
        return f'<Exception of {self.exception!r}>'

    def string_traceback(self):
        context = self.context
        position = self.position

        no_colored = context.flags & NO_COLOR
        colored = not no_colored

        if no_colored:
            reset = ''
            magenta = ''
            bmagenta = ''
        else:
            reset = acolor('reset')
            magenta = acolor('magenta')
            bmagenta = acolor('magenta', BOLD)

        frames = []

        while context:
            is_positionless = position.is_positionless
            context_name = context.name

            frames.append(
                f'  File {magenta}"{position.file.name}"{reset}'
                '{}{}{}'.format(
                    '' if is_positionless else f', line {magenta}{position.start_line}{reset}',
                    '' if context_name is None else f', in {magenta}{context_name}{reset}',
                    '' if is_positionless else f'\n{space_indent(position.format_arrow(colored), 4)}'
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
                    strings_traceback += f'  [Previous line repeated {found_duplicated_frame} more times]\n'
                    found_duplicated_frame = 0

                strings_traceback += frame + '\n'
                last_frame = frame

        if found_duplicated_frame > 0:
            strings_traceback += f'  [Previous line repeated {found_duplicated_frame} more times]\n'

        result = f'Traceback (most recent call last):\n{strings_traceback}'

        if isinstance(self.exception, type):
            result += f'{bmagenta}{self.exception.__name__}{reset}'
        else:
            message = str(self.exception)
            result += (
                f'{bmagenta}{type(self.exception).__name__}{reset}' +
                (f': {magenta}{message}{reset}' if message else '')
            )

        return (
            f'{self.other.string_traceback()}\n\n'
            'During handling of the above exception, another exception occurred:'
            f'\n\n{result}'
            if self.other else
            result
        )

class PysShouldReturn(Pys, BaseException):

    __slots__ = ('result',)

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
        return type(exception).__name__ + (f': {message}' if message else '')