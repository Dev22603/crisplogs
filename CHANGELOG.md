# Changelog

All notable changes to `crisplogs` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> See the [GitHub Releases](https://github.com/dev22603/crisplogs/releases)
> page for download artifacts and any extra release context.

## [Unreleased]

## [0.3.0] - 2026-05-05

### Added
- `crisplogs.types` module exporting `Level`, `Style`, `ExtraFormat`,
  `Width`, and `LogColors` type aliases. All re-exported from the package
  root for users to annotate their own code.
- `crisplogs.exceptions` module with a typed exception hierarchy:
  `CrisplogsError` (base), `InvalidLevelError`, `InvalidStyleError`,
  `InvalidColorError`, `InvalidExtraFormatError`, `InvalidWidthError`. Each
  subclass also inherits from `ValueError` so existing `except ValueError`
  callers keep working.
- `__repr__` on `LogFormatter` and `CleanFileHandler` so REPL exploration
  and debug logging show useful state.
- `AGENTS.md` at the repo root with canonical imports, antipatterns, and
  the color-string grammar for AI coding assistants.
- `CHANGELOG.md` (this file). The `pyproject.toml` `Changelog` URL still
  points at GitHub releases; the file in the repo is the authoritative
  per-version log shipped in the source distribution.
- Validation of `style` and `extra_format` arguments in `setup_logging` and
  `LogFormatter` constructor.
- "Common Pitfalls" section in the README and a versioning note about 0.x.

### Changed
- **BREAKING:** `setup_logging` now takes only keyword arguments. Any
  positional call site needs to be migrated to keyword form.
- **BREAKING:** `setup_logging` argument types narrowed from `str`/`int` to
  `Literal` aliases. Code that previously passed values like `"info"` (wrong
  case) or `style="boxed"` will now fail at type-check time and raise the
  appropriate typed exception at runtime instead of a generic `ValueError`.
- Validation messages reformatted for clarity (e.g. ``level must be one of
  'DEBUG', 'INFO', ...; got 'VERBOSE'``).
- Docstrings on every public symbol expanded to match README depth, with
  Args/Returns/Raises/Example sections in Google style.

### Fixed
- `width="auto"` is now accepted by `setup_logging` (previously only valid
  via direct `LogFormatter` use).

## [0.2.0] - 2025

### Added
- Zero runtime dependencies.
- Single `LogFormatter` covering all output styles via constructor options.
- Logger registry with `setup_logging`, `get_logger`, `reset_logging`,
  `remove_logger`.
- `CleanFileHandler` that strips ANSI codes for file output.
- `examples/` directory with 10 runnable scripts covering basic use, box
  styles, custom colors, extras, file logging, level filtering, named
  loggers, plain output, custom date format, and a full demo.
- `py.typed` marker and `Typing :: Typed` classifier.
- Test suite covering colors, formatters, handlers, setup, and utils.

## [0.1.x]

Pre-history; see [GitHub releases](https://github.com/dev22603/crisplogs/releases)
for any artifacts.

[Unreleased]: https://github.com/dev22603/crisplogs/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/dev22603/crisplogs/releases/tag/v0.3.0
[0.2.0]: https://github.com/dev22603/crisplogs/releases/tag/v0.2.0
