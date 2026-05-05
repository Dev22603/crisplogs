# AGENTS.md

Guidance for AI coding assistants using `crisplogs` in user code.

## Canonical imports

For 95% of cases, import only from the package root:

```python
from crisplogs import setup_logging, get_logger
```

For typed user code, the type aliases are also exported:

```python
from crisplogs import Level, Style, ExtraFormat, Width, LogColors
```

For advanced custom-formatter or custom-handler use:

```python
from crisplogs import LogFormatter, CleanFileHandler
```

For exception handling:

```python
from crisplogs import (
    CrisplogsError,
    InvalidLevelError,
    InvalidStyleError,
    InvalidColorError,
    InvalidExtraFormatError,
    InvalidWidthError,
)
```

## The one-call pattern (do this first)

```python
from crisplogs import setup_logging

logger = setup_logging(level="INFO")
logger.info("server started")
```

`setup_logging` returns a configured `logging.Logger` and registers it. Call
it once at application startup. All arguments are keyword-only.

## Named loggers (use after setup_logging)

```python
from crisplogs import setup_logging, get_logger

setup_logging(level="INFO")  # configure root once
db = get_logger("db")         # named child logger
db.info("connected")           # tagged [db] in output
```

## Non-obvious behaviors

- **Extras and short box styles**: structured `extra={...}` data is rendered
  only in the default style and `long-boxed` style. The `short-fixed` and
  `short-dynamic` styles intentionally drop extras to preserve layout
  alignment. If a user wants to log structured data inside a box, use
  `style="long-boxed"`.
- **File output strips ANSI**: writing to a file via `file="path.log"`
  automatically strips color codes. The same logger can simultaneously emit
  colored output to console and clean text to file.
- **`capture_caller_info=False` for hot paths**: caller-info capture inspects
  stack frames on every log call. Disable in high-throughput code; logs will
  show `<unknown>:0` instead of real `file:line`.
- **`reset_logging()` in tests**: pytest fixtures should call
  `reset_logging()` in teardown to avoid handler leaks across tests.

## Antipatterns

- Do not call `setup_logging()` multiple times in the same process unless you
  intend to reconfigure. The package clears the previous handlers for the
  same `name`, but reconfiguring obscures intent. Use `reset_logging()`
  explicitly when you mean to start fresh.
- Do not pass lowercase levels (`"info"`, `"debug"`). Levels are uppercase:
  `"INFO"`, `"DEBUG"`. The `Level` type enforces this at type-check time and
  `setup_logging` raises `InvalidLevelError` at runtime.
- Do not import from internal modules (anything starting with `_`). The
  public API is the package root only.
- Do not subclass `LogFormatter` to change behavior; pass options instead.
  Subclassing is not a supported extension point.
- Do not pass positional arguments to `setup_logging`. Every parameter is
  keyword-only.

## Color string format

Format: `[modifier_]color[,bg_color]`

- Colors: `black`, `red`, `green`, `yellow`, `blue`, `purple`/`magenta`,
  `cyan`, `white`
- Modifiers: `bold_`, `thin_`, `dim_`, `italic_`, `underline_`
- Backgrounds: `bg_black`, `bg_red`, `bg_green`, `bg_yellow`, `bg_blue`,
  `bg_purple`/`bg_magenta`, `bg_cyan`, `bg_white`

Valid examples: `"green"`, `"bold_red"`, `"bold_white,bg_red"`
Invalid: `"GREEN"` (case), `"bright_red"` (unknown modifier),
`"red,red"` (no `bg_` prefix on background)

## Exception handling

All errors crisplogs raises inherit from both `CrisplogsError` and
`ValueError`:

```python
from crisplogs import setup_logging, CrisplogsError, InvalidLevelError

try:
    logger = setup_logging(level="info")  # wrong case
except InvalidLevelError as e:
    print(f"bad level: {e}")
except CrisplogsError as e:
    print(f"crisplogs config error: {e}")
```

Catch `CrisplogsError` to handle any package error generically, or specific
subclasses (`InvalidLevelError`, `InvalidStyleError`,
`InvalidExtraFormatError`, `InvalidWidthError`, `InvalidColorError`) for
fine-grained handling.

## Versioning

Currently 0.x: breaking changes possible between minor versions. Pin to a
minor version (`crisplogs~=0.3.0`) until 1.0.0 is released. See
`CHANGELOG.md` for the full version history.
