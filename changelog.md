# Change Log

## [1.11.0] - 01/02/2026

### Added
- Argument flag `-O` (aka `-d`).
- Builtin functions `copyright()` and `credits()`.
- Expressions in dictionary literals, keys and values ​​support walrus operations.
- Additional captures patterns on number literal for pygments.
- New `-l` argument selection choice for pygments.
- The built-in function `require()` does not throw an `ImportError` due to a direct circular import.
- `hook.argv` is not always an empty list (it usually has the value `['']`).
- _etc_.

### Fixed
- **Fixed some bugs**.
- The `fpstimer` library is written in Python for speed efficiency.
- _etc_.