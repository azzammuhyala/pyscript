# Change Log

## [1.6.0a1] - 28-11-2025

### Added
- New nodes `PysDictionaryNode`, `PysSetNode`, `PysListNode`, `PysTuple`, `PysStatementsNode`, `PysGlobalNode`, and
  `PysDeleteNode`.
- The `require()` builtin supports attribute component operations with the `>` sign.
- The `pyimport()` builtin automatically adds a new path to `sys.path` based on the file where the function is called.
- Some built-in library modules.
- Walrus operation (`:=`).
- `from` keyword in `throw` (cause of exception)
- _etc_.

### Fixed
- All `TOKENS` names changed.
- Tokenize encoding literal bytes. (`'ascii'` -> `'latin-1'`).
- Runtime delete.
- Runtime speed improvements.
- Parsing in `if` and `switch`.
- Parsing in assignment operation.
- Tokenize prefix string (`r` and `b`).
- _etc_.

### Deleted
- Node `PysSequenceNode`.