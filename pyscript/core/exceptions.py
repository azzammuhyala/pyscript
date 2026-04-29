from .bases import Pys
from .constants import NO_COLOR
from .utils.decorators import immutable
from .utils.generic import setimuattr
from .utils.string import indent

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .context import PysContext
    from .position import PysPosition
    from .results import PysRunTimeResult

@immutable
class PysTraceback(Pys):

    __slots__ = ('exception', 'context', 'position', 'primary', 'implicit')

    def __init__(
        self,
        exception: BaseException | type[BaseException],
        context: 'PysContext',
        position: 'PysPosition',
        primary: Optional['PysTraceback'] = None,
        implicit: bool = False
    ) -> None:
        # circular import problem solved
        from .cache import pys_sys

        setimuattr(self, 'exception', exception)
        setimuattr(self, 'context', context)
        setimuattr(self, 'position', position)
        setimuattr(self, 'primary', primary)
        setimuattr(self, 'implicit', implicit)

        pys_sys.last_type = type(exception) if isinstance(exception, BaseException) else exception
        pys_sys.last_value = exception if isinstance(exception, BaseException) else None
        pys_sys.last_traceback = self

    def __repr__(self) -> str:
        return f'<traceback of {self.exception!r}>'

    def string_traceback(self) -> str:
        # circular import problem solved
        from .mapping import GET_ACOLOR
        from .position import format_error_arrow

        context = self.context
        position = self.position
        colored = not (context.flags & NO_COLOR)

        if colored:
            reset = GET_ACOLOR('reset')
            magenta = GET_ACOLOR('magenta')
            bmagenta = GET_ACOLOR('bold-magenta')
        else:
            reset = ''
            magenta = ''
            bmagenta = ''

        frames = []

        while context:
            is_positionless = position.is_positionless
            context_name = context.name

            frames.append(
                f'  File {magenta}"{position.file.name}"{reset}' +
                ('' if is_positionless      else f', line {magenta}{position.start_line}{reset}') + 
                ('' if context_name is None else f', in {magenta}{context_name}{reset}') +
                ('' if is_positionless      else f'\n{indent(format_error_arrow(position, colored), 4)}')
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
            result += f'{bmagenta}{type(self.exception).__name__}{reset}'
            if message:
                result += f': {magenta}{message}{reset}'

        return (
            (
                f'{self.primary.string_traceback()}\n\n' + (
                    "The above exception was the direct cause of the following exception"
                    if self.implicit else
                    "During handling of the above exception, another exception occurred"
                ) + f':\n\n{result}'
            ) if self.primary else result
        )

class PysSignal(Pys, BaseException):

    __slots__ = ('result',)

    def __init__(self, result: 'PysRunTimeResult') -> None:
        super().__init__()
        self.result = result

    def __str__(self) -> str:
        return '<signal>' if (error := self.result.error) is None else (
            exception.__name__
            if isinstance(exception := error.exception, type) else
            type(exception).__name__ + (f': {message}' if (message := str(exception)) else '')
        )