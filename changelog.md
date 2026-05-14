# Change Logs

## [1.13.0] - 14/05/2026

### Added
- The `else` keyword is used in `match` as an alias for the `default` keyword.
- The `pyscript.core.pystypes.PysPythonFunction` passes two parameters, `context` and `position`, instead of passing one
  parameter to itself.
- In the symbol table object, `__builtins__` has its own namespace named `builtins`.
- Direct deletion of the global namespace with the `/clean` command. This allows the _Python Garbage Collector_ to
  immediately delete all objects in that namespace.
- A single statement will directly provide that single node instead of providing a
  `pyscript.core.nodes.PysStatementsNode`.
- A new mechanism for getting built-in module import functions in `import` and `from` statements.
- The keywords `in`, `is`, `and`, `or`, `not`, and `typeof` are not available in `PysToken` (new token types).
- The `instanceof` keyword (same as the built-in `isinstance()` function).
- _etc._

### Fixed
- Add word boundary `'\b'` to number regex.
- Add of information in the parser in the form of rows and columns.
- Fixed some bugs.
- _etc._

### Deleted
- `pyscript.core.mapping.EMPTY_MAP`.
- _etc._