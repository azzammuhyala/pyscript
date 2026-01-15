# Change Log

## [1.10.0] - 15/1/2026

### Added
- `ast.literal_eval()` addition arith operations (`+`, and `-`), ellipsis (`...`), constants `inf`, and `nan`.
- New operation symbols for `in` (`->`) and `not in` (`!>`).
- New statement `repeat-until`.
- New alias keywords `except`, `raise`, `null` (same as `None`), and `nil` (same as `None`).
- The catured exceptions can be wrapped into 1 part.
- New future `dict_to_jsdict` / `dict2jsdict`.
- Key and value separators in `dict` can be use with `=`.
- `parser_flags` for parser flags.
- New builtin `unpack()`.
- `increment()` and `decrement()` supports sequence objects in the form of (`list`, `tuple`, and `set`).
- Addition of argument highlight themes `-l`
- _etc_.

### Fixed
- Fixed some bugs.
- Changed the name of the `ansi` module from `fansi` to `ahtml`.
- Highlighting improvements.
- `brainfuck` optimizations.
- _etc_.

## Removed
- Future `reverse_pow_xor`.
- _etc_.