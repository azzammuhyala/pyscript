# Change Log

## [1.7.0] - 10/12/2025

### Added
- Support for the `NO_COLOR` enviroment.
- `pyscript.core.utils.shell`.
- Visual Studio Code extension for syntax highlighting. See more
  [here](https://marketplace.visualstudio.com/items?itemName=azzammuhyala.pyslang).
- `PygmentsPyScriptLexer` object (`pygments` module required).
- Builtin `breakpoint()` (spesific to PyScript).
- `'single'` mode in `pys_runner()`
- `flags` parameter in `pys_require()`
- `ansi` module.

### Fixed
- Error message fixes.
- Error shell (REPL) fixes on non-Windows platforms using `import readline`
- PyScript default environment.
- `jsdict` and `fpstimer` module fixes.
- `handlers` fixes.

### Removed
- `pyscript.core.handlers.handle_exception`
- `pyscript.core.handlers.handle_execute`