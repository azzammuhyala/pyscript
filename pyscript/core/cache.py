from .singletons import PysHook

loading_modules = set()
library = set()
modules = {}
hook = PysHook()

del PysHook