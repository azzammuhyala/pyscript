from .constants import LIBRARY_PATH
from .utils import get_name

import os
import sys

loading_modules = set()

try:
    library = set(os.path.splitext(lib)[0] for lib in os.listdir(LIBRARY_PATH))
except BaseException as e:
    library = set()
    print("can't access directory {!r}: {}: {}".format(LIBRARY_PATH, get_name(e), e), file=sys.stderr)

modules = dict()
hook = None