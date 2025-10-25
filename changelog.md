# Change Log

## [1.3.0] - 25-10-2025

### Added
- `pyscript.core.position.PysPosition.is_positionless()`, check a `PysPosition` object whether it has a position or not
  (A position will be considered to exist if the `start` and `end` indexes are positive and `start` less than `end`).
- `else` block in the `try` block. Executed when the `try` block succeeds without an exception.
- `pyscript.core.parser.PysParser.incremental`, evaluates the increment `++`, and decrement `--` expressions right-hand
  side operations.
- `require('sys').executable`, shell executable.
- `require('sys').hook.ps1`, a main string prompt on an interactive shell.
- `require('sys').hook.ps2`, a continuation string prompt on an interactive shell.
- Conditional expressions can be written directly without parentheses.
- Keywords `true` (A.K.A `True`), `false` (A.K.A `False`), and `none` (A.K.A `None`).
- Library `jsdict`, dict object that imitates an object (dictionary) in JavaScript.
- Separate documentation.
- Statement `global`, allows assign and delete the value of the outer variable scope.

### Fixed
- Change name `pyscript.core.validator.PysValidator` to `pyscript.core.analyzer.PysAnalyzer`.
- `flags` moved to `pyscript.core.context.PysContext`.
- `pyscript.core.lexer.PysLexer` improvements.
- `pyscript.core.interpreter.PysInterpreter` improvements and performances.
- `pyscript.core.parser.PysParser` improvements.
- `pyscript.core.objects` improvements.
- `pyscript.core.pysbuiltins` improvements.
- `pyscript.core.symtab.PysSymbolTable` improvements.
- `pyscript.core.utils` improvements.