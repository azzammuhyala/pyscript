# Change Logs

## [1.13.4] - 01/09/2026

### Added
- Added comparison support for complex objects in the builtin `ce` and `nce` functions.
- Default maximum input history lines for Pygments to 2048.
- Configured `open()` encoding based on `pys_sys.encoding` (PyScript `sys.encoding`).
- The `else` keyword is alias for `default` in `switch` statements.
- The `fpstimer` module now stores the default framerate value.
- Added `NO_WARNING` flag.
- _etc._

### Fixed
- Fixed some bugs.
- The builtins `inf`, `infj`, `nan`, and `nanj` come from the `cmath` module.
- _etc._

### Removed
- The attributes of `pys_sys` namely `last_type`, `last_value`, and `last_traceback`.