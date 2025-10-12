from .singletons import PysVersionInfo

__version__ = '1.2.3'
__date__ = '12 October 2025, 13:15 UTC+7'

version = '{} ({})'.format(__version__, __date__)
version_info = PysVersionInfo()

del PysVersionInfo