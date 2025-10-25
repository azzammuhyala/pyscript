from typing import TYPE_CHECKING, Any, Callable, Dict, Literal, Union, Optional, Tuple

if TYPE_CHECKING:
    from .core.buffer import PysFileBuffer
    from .core.highlight import _HighlightFormatter
    from .core.position import PysPosition
    from .core.results import PysExecuteResult
    from .core.symtab import PysSymbolTable

    from io import IOBase

from . import core

DEFAULT: int
OPTIMIZE: int
SILENT: int
RETRES: int
COMMENT: int
REVERSE_POW_XOR: int

HLFMT_HTML: _HighlightFormatter
HLFMT_ANSI: _HighlightFormatter

def pys_highlight(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    format: Optional[Callable[[
        Literal[
            'start',
            'bracket-unmatch',
            'identifier', 'identifier-const', 'identifier-call', 'identifier-class',
            'keyword', 'keyword-identifier',
            'number', 'string', 'comment', 'newline',
            'default',
            'end'
        ], PysPosition, str], str]] = None,
    max_parenthesis_level: int = 3,
    flags: int = COMMENT
) -> str: ...

def pys_exec(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    globals: Optional[Union[Dict[str, Any], PysSymbolTable]] = None,
    flags: int = DEFAULT
) -> Union[None, PysExecuteResult]: ...

def pys_eval(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    globals: Optional[Union[Dict[str, Any], PysSymbolTable]] = None,
    flags: int = DEFAULT
) -> Union[Any, PysExecuteResult]: ...

__version__: str
__date__: str
__all__: Tuple[str]