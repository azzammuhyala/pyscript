# Change Log

## [1.2.3] - 12-10-2025

### Added
- `qualname` on `pyscript.core.context.PysContext`.
- Flag `COMMENT` (replace `allowed_comment_token` on `pyscript.core.lexer.PysLexer`).

### Fixed
- `pyscript.__main__` improvements.
- `pyscript.core.exceptions` improvements.
- `pyscript.core.handlers` improvements.
- `pyscript.core.objects` improvements.
- `pyscript.core.buffer.PysCode` object are moved to `pyscript.core.objects`
- `pyscript.core.interpreter.PysInterpreter` improvements.
- `pyscript.core.lexer.PysLexer` improvements.
- `pyscript.core.parser.PysParser` improvements.
- `pyscript.core.position.PysPosition` improvements.
- `pyscript.core.results.PysExecuteResult` improvements.
- `pyscript.core.utils.format_highlighted_text_with_arrow` function are moved to `pyscript.core.position.PysPosition`
  A.K.A function method with name `format_arrow`.
- `pyscript.core.utils.generate_string_traceback` function are moved to `pyscript.core.exceptions.PysException`
  A.K.A function method with name `string_traceback`.
- Name changes on all objects in `pyscript.core.singletons`.

### Removed
- Function `pyscript.core.utils.get_line_column_by_index`
- Function `pyscript.code.utils.sanitize_newline`.