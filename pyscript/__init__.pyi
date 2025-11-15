from typing import TYPE_CHECKING, Any, Callable, Iterator, Literal, Optional

if TYPE_CHECKING:
    from .core.buffer import PysFileBuffer
    from .core.cache import PysUndefined
    from .core.highlight import _HighlightFormatter
    from .core.position import PysPosition
    from .core.results import PysExecuteResult
    from .core.symtab import PysSymbolTable
    from .core.version import PysVersionInfo

    from io import IOBase

from . import core as core

DEFAULT: int
DEBUG: int
SILENT: int
RETRES: int
COMMENT: int
NO_COLOR: int
REVERSE_POW_XOR: int

HLFMT_HTML: _HighlightFormatter
HLFMT_ANSI: _HighlightFormatter

undefined: PysUndefined
version_info: PysVersionInfo

def pys_highlight(
    source: str | bytes | bytearray | Iterator | Callable | IOBase | PysFileBuffer,
    format: Optional[
        Callable[
            [
                str | Literal[
                    'start',
                    'bracket-unmatch',
                    'identifier', 'identifier-const', 'identifier-call', 'identifier-class',
                    'keyword', 'keyword-identifier',
                    'number', 'string', 'comment', 'newline',
                    'default',
                    'end'
                ],
                PysPosition,
                str
            ],
            str
        ]
    ] = None,
    max_parenthesis_level: int = 3,
    flags: int = DEFAULT
) -> str: ...

def pys_exec(
    source: str | bytes | bytearray | Iterator | Callable | IOBase | PysFileBuffer,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> None | PysExecuteResult: ...

def pys_eval(
    source: str | bytes | bytearray | Iterator | Callable | IOBase | PysFileBuffer,
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> Any | PysExecuteResult: ...

def pys_shell(
    globals: Optional[dict[str, Any] | PysSymbolTable | PysUndefined] = None,
    flags: int = DEFAULT
) -> int | Any: ...

__version__: str
__date__: str
__all__: tuple[str]