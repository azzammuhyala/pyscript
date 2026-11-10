# Change Logs

## [1.15.3] - 10/11/2026

### Added
- Some functions in the `site` library now raise exceptions if `ENABLE_USER_SITE` is `None`.
- _etc._

### Fixed
- The user site-packages path has been moved to `site.getusersitepackages()` + `/pyscript/site-packages`.
- The **Shift** + **Tab** shortcut now performs a dedent to the one tab character.
- Fixed several bugs.
- _etc._