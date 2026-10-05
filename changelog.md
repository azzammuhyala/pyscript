# Change Logs

## [1.14.0] - 05/10/2026

### Added
- All editors are not loaded when PyScript is loaded.
- `pys_sys` is available in the main `__init__`.
- The `import` statement can import several modules at once with a comma (`,`) as separator.
- Display of help, error, etc. arguments in argparser can be colored and not from `-n` / `--no-color` arguments.
- _etc._

### Fixed
- Fixed some bugs.
- `PysContext`, `PysSymbolTable`, and `PysTraceback` are now mutable for performance.
- Environ `PYSCRIPT_NO_GIL` changed to `PYSCRIPT_WITH_GIL` (default without GIL).
- _etc._

### Removed
- The `NotImplementedError` exception is not catch by the builtin function as a sign that the object does not support an
  operation.
- _etc._