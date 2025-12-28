# Change Log

## [1.9.0] - 28/12/2025

### Added
- Class `pyscript.core.objects.PysBuiltinFunction` (builtins from PyScript are wrapped with this).
- The `constructor` keyword (an alternative to the `func __init__(self, ...)` code).
- Added type hints on some objects.
- Builtin `ce()` supports a method called `__nce__` (negated).
- Keyword `match` now tolerates the absence of a condition.
- Builin `breakpoint()` added new commands and ansi prompt support.

### Fixed
- Fixed some bugs.
- Fixed syntax highlight.