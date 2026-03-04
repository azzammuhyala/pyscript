from .bases import Pys
from .constants import PYSCRIPT_PATH, CORE_PATH, LIBRARIES_PATH, SITE_PACKAGES_PATH, DEFAULT
from .utils.debug import print_display, print_traceback, clear_shell
from .utils.decorators import inheritable, singleton

from typing import Literal
from types import ModuleType

import sys

pys_sys = ModuleType(
    'sys',
    "This is a sys module for PyScript, which provides necessary attributes, functions, and objects for the PyScript "
    "environment. It is designed to be used within the PyScript runtime and should not be confused with the standard "
    "Python sys module."
)

pys_sys.__running_shell__ = False
pys_sys.__running_breakpoint__ = False
pys_sys.argv = ['']
pys_sys.flags = DEFAULT
pys_sys.displayhook = print_display
pys_sys.excepthook = print_traceback
pys_sys.clearhook = clear_shell
pys_sys.exec_prefix = pys_sys.prefix = pys_sys.pyscript_path = PYSCRIPT_PATH
pys_sys.core_path = CORE_PATH
pys_sys.libraries_path = LIBRARIES_PATH
pys_sys.site_packages_path = SITE_PACKAGES_PATH
pys_sys.executable = f'"{sys.executable}" -m pyscript'
pys_sys.ps1 = '>>> '
pys_sys.ps2 = '... '
pys_sys.float_info = sys.float_info
pys_sys.int_info = sys.int_info
pys_sys.hash_info = sys.hash_info
pys_sys.stderr = sys.stderr
pys_sys.stdout = sys.stdout
pys_sys.stdin = sys.stdin
pys_sys.platform = sys.platform
pys_sys.exit = sys.exit
pys_sys.getrecursionlimit = sys.getrecursionlimit
pys_sys.getrefcount = sys.getrefcount
pys_sys.getsizeof = sys.getsizeof
pys_sys.setrecursionlimit = sys.setrecursionlimit

# added in python>=3.10.7
if hasattr(sys, 'get_int_max_str_digits') and hasattr(sys, 'set_int_max_str_digits'):
    pys_sys.get_int_max_str_digits = sys.get_int_max_str_digits
    pys_sys.set_int_max_str_digits = sys.set_int_max_str_digits

pys_sys.path = [SITE_PACKAGES_PATH, LIBRARIES_PATH]
pys_sys.loading_modules = set()
pys_sys.modules = {}
pys_sys.singletons = {}

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