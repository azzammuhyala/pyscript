from .bases import Pys
from .cache import pys_sys
from .constants import DEFAULT
from .context import PysContext
from .exceptions import PysTraceback, PysSignal
from .nodes import PysNode
from .position import PysPosition
from .utils.debug import print_traceback, get_error_args

from types import TracebackType
from typing import Any, Literal, Union

class PysResult(Pys):
    __slots__ = ()

class PysParserResult(PysResult):

    __slots__ = ('last_registered_advance_count', 'advance_count', 'to_reverse_count', 'fatal', 'node', 'error')

    def __init__(self) -> None:
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0
        self.fatal = False
        self.node = None
        self.error = None

    def register_advancement(self) -> None:
        self.last_registered_advance_count += 1
        self.advance_count += 1

    def register(self, result: 'PysParserResult', require: bool = False) -> PysNode:
        self.last_registered_advance_count = result.advance_count
        self.advance_count += result.advance_count
        self.fatal = require or result.fatal
        self.error = result.error
        return result.node

    def try_register(self, result: 'PysParserResult') -> Union['PysParserResult', None]:
        if result.error and not result.fatal:
            self.to_reverse_count = result.advance_count
        else:
            return self.register(result)

    def success(self, node: PysNode) -> 'PysParserResult':
        self.node = node
        return self

    def failure(self, error: PysTraceback, fatal: bool = True) -> 'PysParserResult':
        if not self.error or self.last_registered_advance_count == 0:
            self.fatal = fatal
            self.node = None
            self.error = error
        return self

class PysRunTimeResult(PysResult):

    __slots__ = (
        'should_continue', 'should_break', 'func_should_return', 'func_return_value', 'value', 'error',
        '_context', '_position'
    )

    def reset(self) -> bool:
        self.should_continue = False
        self.should_break = False
        self.func_should_return = False
        self.func_return_value = None
        self.value = None
        self.error = None

    __init__ = reset

    def register(self, result: 'PysRunTimeResult') -> Any:
        self.error = result.error
        self.should_continue = result.should_continue
        self.should_break = result.should_break
        self.func_should_return = result.func_should_return
        self.func_return_value = result.func_return_value
        return result.value

    def success(self, value: Any) -> 'PysRunTimeResult':
        self.reset()
        self.value = value
        return self

    def success_return(self, value: Any) -> 'PysRunTimeResult':
        self.reset()
        self.func_should_return = True
        self.func_return_value = value
        return self

    def success_continue(self) -> 'PysRunTimeResult':
        self.reset()
        self.should_continue = True
        return self

    def success_break(self) -> 'PysRunTimeResult':
        self.reset()
        self.should_break = True
        return self

    def failure(self, error: PysTraceback) -> 'PysRunTimeResult':
        self.reset()
        self.error = error
        return self

    def should_return(self) -> bool:
        return (
            self.error or
            self.func_should_return or
            self.should_continue or
            self.should_break
        )

    # --- HANDLE EXCEPTION ---

    def __call__(self, context: PysContext, position: PysPosition) -> 'PysRunTimeResult':
        self._context = context
        self._position = position
        return self

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> Literal[True]:
        # return
        # ^^^^^^  <--- debug only

        if exc_type is not None:

            self.register(exc_val.result) \
            if exc_type is PysSignal else \
            self.failure(
                PysTraceback(
                    exc_type if exc_val is None else exc_val,
                    self._context,
                    self._position
                )
            )

        return True

class PysExecuteResult(PysResult):

    __slots__ = ('context', 'parser_flags', 'value', 'error')

    def __init__(self, context: PysContext, parser_flags: int = DEFAULT) -> None:
        self.context = context
        self.parser_flags = parser_flags
        self.value = None
        self.error = None

    def success(self, value: Any) -> 'PysExecuteResult':
        self.value = value
        self.error = None
        return self

    def failure(self, error: PysTraceback) -> 'PysExecuteResult':
        self.value = None
        self.error = error
        return self

    # --- HANDLE EXECUTE ---

    def end_process(self) -> tuple[int | Any, bool]:
        result = PysRunTimeResult()

        with result(self.context, PysPosition(self.context.file, -1, -1)):

            if self.error:
                if self.error.exception is SystemExit:
                    return 0, True
                elif type(self.error.exception) is SystemExit:
                    return self.error.exception.code, True
                elif (excepthook := pys_sys.excepthook) is not None:
                    excepthook(*get_error_args(self.error))
                return 1, False

        if result.should_return():
            if result.error:
                print_traceback(*get_error_args(result.error))
            return 1, False

        return 0, False