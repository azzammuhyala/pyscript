from .bases import Pys
from .constants import PYSCRIPT_PATH, CORE_PATH, LIBRARIES_PATH, SITE_PACKAGES_PATH, DEFAULT
from .utils.debug import print_display, print_traceback, clear_shell
from .utils.decorators import inheritable, singleton
from .utils.path import base

from types import ModuleType
from typing import Literal

import sys

pys_sys = ModuleType(
    'sys',
    "This is a sys module for PyScript, which provides necessary attributes, functions, and objects for the PyScript "
    "environment. It is designed to be used within the PyScript runtime and should not be confused with the standard "
    "Python sys module."
)

pys_sys.__running_shell__ = False
pys_sys.__running_breakpoint__ = False
pys_sys.path = [LIBRARIES_PATH, SITE_PACKAGES_PATH]
pys_sys.loading_modules = set()
pys_sys.modules = {}
pys_sys.singletons = {}
pys_sys.argv = ['']
pys_sys.flags = DEFAULT
pys_sys.displayhook = print_display
pys_sys.excepthook = print_traceback
pys_sys.clearhook = clear_shell
pys_sys.pyscript_path = PYSCRIPT_PATH
pys_sys.core_path = CORE_PATH
pys_sys.libraries_path = LIBRARIES_PATH
pys_sys.site_packages_path = SITE_PACKAGES_PATH
pys_sys.executable = f'{base(sys.executable)} -m pyscript'
pys_sys.ps1 = '>>> '
pys_sys.ps2 = '... '
pys_sys._is_gil_enabled = lambda : pys_sys.gil

for name in (
    'exit', 'float_info', 'float_repr_style', 'get_int_max_str_digits', 'getdefaultencoding',
    'getfilesystemencodeerrors', 'getfilesystemencoding', 'getrecursionlimit', 'getrefcount', 'getsizeof',
    'gettotalrefcount', 'hash_info', 'hexversion', 'int_info', 'intern', 'maxsize', 'maxunicode', 'platform',
    'set_int_max_str_digits', 'setrecursionlimit', 'stderr', 'stdin', 'stdout', 'thread_info'
):
    if hasattr(sys, name):
        setattr(pys_sys, name, getattr(sys, name))

@singleton
@inheritable
class PysUndefined(Pys):

    __slots__ = ()

    def __new_singleton__(cls) -> 'PysUndefined':
        global undefined
        undefined = super(cls, cls).__new__(cls)
        return undefined

    def __repr__(self) -> Literal['undefined']:
        return 'undefined'

    def __bool__(self) -> Literal[False]:
        return False

PysUndefined()