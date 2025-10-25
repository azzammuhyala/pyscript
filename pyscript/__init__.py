"""
PyScript is a programming language written in Python. \
This language is not isolated and is directly integrated with the Python's library and namespace levels.
"""

import sys

if sys.version_info < (3, 5):
    raise ImportError("Python version 3.5 and above is required to run PyScript")

from . import core

from .core.constants import DEFAULT, OPTIMIZE, SILENT, RETRES, COMMENT, REVERSE_POW_XOR
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, pys_highlight
from .core.runner import pys_exec, pys_eval
from .core.version import __version__, __date__

__all__ = (
    'core',
    'DEFAULT',
    'OPTIMIZE',
    'SILENT',
    'RETRES',
    'COMMENT',
    'REVERSE_POW_XOR',
    'HLFMT_HTML',
    'HLFMT_ANSI',
    'pys_highlight',
    'pys_exec',
    'pys_eval'
)

del sys