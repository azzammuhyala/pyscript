# Change Logs

## [1.15.0.dev1] - 19/10/2026

### Added
- Added line number display to each editor mode.
- In `gui` editor mode, the system now attempts to locate the best available monospace font; a 500ms delay has also been
  introduced before updating syntax highlighting to improve performance.
- The `getch` module now includes `init()`, `quit()`, `kbhit()`, `getwch()`, and `getach()`. Calling `getch()` requires
  an initial call to `init()`, followed by `quit()` upon completion to restore the terminal to its original state.
- Added color-coding for opening and closing delimiters in Pygments syntax highlighting.
- Added the `intern_object` function to `pys_sys`.
- `history.load()` now returns entries ordered from oldest to newest (retrieved from the cache).
- `PysPrinter` is now a subclass of `PysObject` and is recognized as a function by `inspect.isfunction()`
  (PyScript’s `inspect` module).
- Added support for constant folding and AST optimizations.
- Introduced `PysConstantNode` to store constant values ​​directly.
- Added the `dual` library in `lib/`
  (representing dual numbers: $a + b\epsilon$, where $\epsilon^2 = 0$ and $\epsilon \ne 0$).
- _etc._

### Fixed
- Fixed several bugs.
- Limited the maximum number of stored history entries to 1024 to optimize history file read/write operations.
- Renamed the environment variable `PYSCRIPT_MAXIMUM_LINE_HISTORY` to `PYSCRIPT_HISTORY_LIMIT`.
- _etc._

### Removed
- Removed `PysNumberNode`, `PysStringNode`, and `PysKeywordNode`, which have been replaced by `PysConstantNode`.
- _etc._