# Change Log

## [1.4.0] - 01-11-2025

### Added
- Block statement `with`.
- Base classes can be written with `extends` keyword.
- `not` can be written with `!`.
- `pyscript.core.context.PysClassContext`.
- `pyscript.core.utils.get_name`.
- Supports chained exceptions with `pyscript.core.exceptions.PysException.other_exception`.
- Ternary operator can be written with Python's ternary syntax `<valid> if <condition> else <invalid>`.

### Fixed
- `pyscript.core.analyzer.PysAnalyzer` improvements.
- `pyscript.core.cache` improvements.
- `pyscript.core.constants` improvements.
- `pyscript.core.context.PysContext` improvements.
- `pyscript.core.exceptions.PysException` improvements.
- `pyscript.core.handlers.handle_exception` improvements and performance.
- `pyscript.core.interpreter` improvements and performance.
- `pyscript.core.lexer.PysLexer` improvements.
- `pyscript.core.nodes` improvements.
- `pyscript.core.objects` improvements.
- `pyscript.core.parser.PysParser` improvements.
- `pyscript.core.pysbuiltins` improvements and performance.
- `pyscript.core.results` improvements.
- `pyscript.core.runner` improvements.
- `pyscript.core.singletons` improvements.
- `pyscript.core.symtab` improvements.
- Token `PLUS` and `MINUS` changed to `ADD` and `SUB`.

## Removed
- `pyscript.core.interpeter.PysInterpreter` and `pyscript.core.interpreter.interpreter`.
- `pyscript.core.nodes.PysGlobalNode`, changed to `pyscript.core.nodes.PysSequence(type='global')`.
- `pyscript.core.nodes.PysDeleteNode`, changed to `pyscript.core.nodes.PysSequence(type='del')`.