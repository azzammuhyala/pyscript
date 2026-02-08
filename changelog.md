# Change Log

## [1.11.2] - 08/02/2026

### Added
- Abbreviate traceback lines with `...<{LINE} lines>...`. To set the maximum limit set the enviroment named
  `PYSCRIPT_MAXIMUM_TRACEBACK_LINE`
- New alias keyword `elseif` (same as `elif`).
- New shell command `/clean`.
- _etc._

### Fixed
- **Fixed some bugs**.
- Function `untokenize` in `tokenize` library.
- _etc._

### Deleted
- Remove type check support with `typeguard`.