# Change Log

## [1.12.0] - 18/02/2026

### Added
- The `sys` (PyScript) module is fully stored at the Python level (stored in `pyscript.core.cache`).
- The `/clear` shell command support for the **Google Colab** platform.
- The `/clean` shell command resets the `parser_flags` value.
- Adds _insert_, _pageup_, and _pagedown_ key system in the terminal editor.
- Adds new argument flag `-k/--classic-line-shell` and enviroment `PYSCRIPT_CLASSIC_LINE_SHELL`.
- Interactive shell input is supported and is the default with `prompt_toolkit`.
- Using a new way to wrap and configure this packages with `pyproject.toml`.
- _etc_.

### Fixed
- **Fixed some bugs**.
- _etc._

### Removed
- `pyscript.core.cache.PysHook` object.
- _etc_.