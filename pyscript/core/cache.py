from .constants import LIBRARY_PATH

import os
import sys

loading_modules = set()

try:
    library = set(os.path.splitext(lib)[0] for lib in os.listdir(LIBRARY_PATH))
except BaseException as e:
    library = set()
    print("Error: can't access directory {!r}: {}".format(LIBRARY_PATH, e), file=sys.stderr)

modules = dict()
hook = None