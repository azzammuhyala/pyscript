from .singletons import VersionInfo

__version__ = '1.2.0'
__date__ = '4 October 2025, 14:30 UTC+7'

version = '{} ({})'.format(__version__, __date__)
version_info = VersionInfo()

del VersionInfo