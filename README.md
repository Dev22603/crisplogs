<p align="center">
  <h1 align="center">crisplogs</h1>
  <p align="center">Beautiful, structured terminal logging for Python</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/crisplogs/"><img src="https://img.shields.io/badge/pypi-v0.3.0-blue.svg" alt="PyPI version"></a>
  <a href="https://github.com/dev22603/crisplogs/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="license"></a>
  <img src="https://img.shields.io/badge/python-%3E%3D3.8-brightgreen.svg" alt="python version">
  <img src="https://img.shields.io/badge/dependencies-0-green.svg" alt="zero dependencies">
</p>

---

> **Note:** This package is in 0.x. Minor version bumps may include breaking changes. Pin to `crisplogs~=0.3.0` for stability until 1.0.0.

One function call to get production-ready logs with colors, box decorations, structured data, and file output. Zero runtime dependencies.

```python
from crisplogs import setup_logging

logger = setup_logging()

logger.info("Server started on port 8000")
logger.warning("Disk usage at 85%", extra={"mount": "/dev/sda1"})
logger.error("Connection failed", extra={"host": "db.internal", "retries": 3})
```

```
INFO     2025-09-08 12:30:45 [root] app.py:5 - Server started on port 8000
WARNING  2025-09-08 12:30:45 [root] app.py:6 - Disk usage at 85% [mount=/dev/sda1]
ERROR    2025-09-08 12:30:45 [root] app.py:7 - Connection failed [host=db.internal retries=3]
```

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Output Styles](#output-styles)
- [Options](#options)
- [Structured Data (Extras)](#structured-data-extras)
- [File Logging](#file-logging)
- [Named Loggers](#named-loggers)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [License](#license)

## Installation

```bash
pip install crisplogs
```

## Quick Start

```python
from crisplogs import setup_logging

logger = setup_logging()

logger.debug("Loading configuration...")
logger.info("Server started on port 8000")
logger.warning("Disk usage at 85%")
logger.error("Failed to connect to database")
logger.critical("System is shutting down")
```

All five log levels are supported: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

## Output Styles

crisplogs ships with four output styles. Set the `style` option to switch between them.

### Default (no box)

Colored single-line output. Each level gets its own color.

```python
logger = setup_logging()  # or style=None
```

```
INFO     2025-09-08 12:30:45 [root] app.py:5 - Server started
WARNING  2025-09-08 12:30:46 [root] app.py:6 - Disk usage high
ERROR    2025-09-08 12:31:12 [root] db.py:45 - Connection failed
```

### `short-fixed`

Fixed-width box with left border. Clean and consistent.

```python
logger = setup_logging(style="short-fixed")
```

```
┌──────────────────────────────────────────────────────────────────────────────────
│ INFO     12:30:45 [root] app.py:5 - Server started
└──────────────────────────────────────────────────────────────────────────────────
```

### `short-dynamic`

Full border that adjusts to fit the message width.

```python
logger = setup_logging(style="short-dynamic")
```

```
┌──────────────────────────────────────────────────────────┐
│ INFO     12:30:45 [root] app.py:5 - Server started       │
└──────────────────────────────────────────────────────────┘
```

### `long-boxed`

Word-wrapped box with left border. Best for long messages and structured data.

```python
logger = setup_logging(style="long-boxed", width=80)
```

```
┌──────────────────────────────────────────────────────────────────────────────────
│ INFO     12:34:56 [root] app.py:10 - This is a long message that wraps neatly
│ across multiple lines without breaking words [user_id=42 action=login]
└──────────────────────────────────────────────────────────────────────────────────
```

### Combining styles with color

All styles work with or without color:

```python
setup_logging(colored=True,  style="long-boxed")   # colored + boxed
setup_logging(colored=False, style="short-fixed")  # plain + boxed
setup_logging(colored=True,  style=None)            # colored, no box
setup_logging(colored=False)                        # plain text
```

## Options

### `setup_logging(**options)`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `colored` | `bool` | `True` | Enable ANSI colors in console output |
| `style` | `"short-fixed"` \| `"short-dynamic"` \| `"long-boxed"` \| `None` | `None` | Box decoration style |
| `level` | `Level` | `"DEBUG"` | Minimum log level for console |
| `width` | `int` | `100` | Box width in characters |
| `datefmt` | `str` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format |
| `log_colors` | `dict` | built-in scheme | Custom colors per level |
| `extra_format` | `"inline"` \| `"json"` \| `"pretty"` | `"inline"` | How structured data is rendered |
| `file` | `str` \| `None` | `None` | Path to log file (ANSI auto-stripped) |
| `file_level` | `Level` \| `None` | same as `level` | Minimum level for file output |
| `name` | `str` | `""` | Logger name (`""` = root logger) |
| `capture_caller_info` | `bool` | `True` | Capture file path and line number |

### Log Levels

| Level | Value | Use for |
|-------|-------|---------|
| `DEBUG` | 10 | Detailed diagnostic information |
| `INFO` | 20 | Routine operational messages |
| `WARNING` | 30 | Something unexpected but recoverable |
| `ERROR` | 40 | A failure that needs attention |
| `CRITICAL` | 50 | System-level failure |

```python
# Only show WARNING and above on console
logger = setup_logging(level="WARNING")

logger.debug("hidden")    # filtered out
logger.info("hidden")     # filtered out
logger.warning("shown")   # displayed
logger.error("shown")     # displayed
```

### Date Format Tokens

| Token | Output | Example |
|-------|--------|---------|
| `%Y` | 4-digit year | `2025` |
| `%m` | Month (01-12) | `09` |
| `%d` | Day (01-31) | `08` |
| `%H` | Hour 24h (00-23) | `14` |
| `%M` | Minute (00-59) | `30` |
| `%S` | Second (00-59) | `45` |
| `%I` | Hour 12h (01-12) | `02` |
| `%p` | AM/PM | `PM` |
| `%f` | Microseconds | `123456` |
| `%%` | Literal `%` | `%` |

```python
setup_logging(datefmt="%H:%M:%S")        # 14:30:45
setup_logging(datefmt="%d/%m/%Y %H:%M")  # 08/09/2025 14:30
setup_logging(datefmt="%I:%M %p")         # 02:30 PM
```

### Custom Colors

Override colors for any log level. Supports basic colors, modifiers, backgrounds, and combinations:

```python
setup_logging(log_colors={
    "DEBUG":    "thin_white",
    "INFO":     "bold_green",
    "WARNING":  "bold_yellow",
    "ERROR":    "bold_red,bg_white",
    "CRITICAL": "bold_white,bg_red",
})
```

**Available colors:** `black`, `red`, `green`, `yellow`, `blue`, `purple`/`magenta`, `cyan`, `white`

**Modifiers:** `bold_`, `thin_`/`dim_`, `italic_`, `underline_`

**Backgrounds:** `bg_red`, `bg_blue`, `bg_white`, etc.

**Combine with commas:** `"bold_red,bg_white"`

<details>
<summary>Default color scheme</summary>

| Level | Color |
|-------|-------|
| `DEBUG` | `cyan` |
| `INFO` | `green` |
| `WARNING` | `yellow` |
| `ERROR` | `red` |
| `CRITICAL` | `bold_red` |

</details>

## Structured Data (Extras)

Attach key-value context to any log message via the `extra` argument:

```python
logger.info("User signed up",  extra={"user_id": 101, "plan": "pro"})
logger.error("Payment failed", extra={"order_id": 5524, "gateway": "stripe"})
```

Control how extras are rendered with the `extra_format` option:

### `"inline"` (default)

```
INFO  ... - User signed up [user_id=101 plan=pro]
```

### `"json"`

```
INFO  ... - User signed up {"user_id": 101, "plan": "pro"}
```

### `"pretty"`

```
INFO  ... - User signed up
{
  "user_id": 101,
  "plan": "pro"
}
```

```python
setup_logging(extra_format="json")
setup_logging(extra_format="pretty", style="long-boxed")  # great combo
```

> **Note:** Extras are rendered in the default (no box) and `long-boxed` styles. Short box styles (`short-fixed`, `short-dynamic`) do not display extras to preserve layout alignment.

## File Logging

Write logs to a file alongside console output. ANSI codes are automatically stripped so log files stay clean.

```python
logger = setup_logging(file="logs/app.log")
```

Set a separate level threshold for the file — useful for verbose console output with a quieter file:

```python
logger = setup_logging(
    level="DEBUG",           # console: show everything
    file="logs/app.log",
    file_level="WARNING",    # file: only WARNING and above
)
```

## Named Loggers

Use named loggers to identify which part of your application produced each message:

```python
from crisplogs import setup_logging, get_logger

# Configure root logger once at startup
setup_logging(level="INFO")

# Get named loggers anywhere in your app
db_logger  = get_logger("db")
api_logger = get_logger("api")

db_logger.info("Connected to PostgreSQL")   # [db]  in output
api_logger.info("Listening on :8080")        # [api] in output
```

Named loggers inherit the root logger's configuration (handlers, formatters). Use `setup_logging(name="...")` to configure a specific logger independently.

## Advanced Usage

### Performance Tuning

Caller info capture (stack frame inspection) runs on every log call. Disable it in high-throughput scenarios:

```python
logger = setup_logging(capture_caller_info=False)
# Logs will show <unknown>:0 instead of real file:line
```

### Check Level Before Logging

Skip expensive serialization when the message would be filtered:

```python
import logging

if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Full state dump", extra={"state": expensive_serialize(app_state)})
```

### Cleanup

```python
from crisplogs import reset_logging, remove_logger

remove_logger("db")   # remove and close one logger
reset_logging()        # close all loggers (useful in tests)
```

### Custom Formatter

Use `LogFormatter` directly for full control:

```python
from crisplogs import LogFormatter

formatter = LogFormatter(
    datefmt="%H:%M:%S",
    log_colors={"INFO": "bold_cyan"},
    colored=True,
    box=True,
    full_border=True,
    width="auto",        # or a fixed integer
    word_wrap=False,
    extra_format="json",
)
```

### Custom Handler

Build on `logging.Handler` for custom destinations (HTTP, database, external service):

```python
import logging
from crisplogs import LogFormatter

class MyHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        # send to your destination
        send_to_external_service(msg)

handler = MyHandler()
handler.setFormatter(LogFormatter(log_colors={}, colored=False, datefmt="%H:%M:%S"))

logger = setup_logging(name="myapp")
logger.addHandler(handler)
```

## Common Pitfalls

- **Extras only render in default and `long-boxed` styles.** Short box styles drop extras for layout reasons.
- **Calling `setup_logging` twice** replaces handlers for that logger name; call `reset_logging()` first if you mean to start completely fresh.
- **Lowercase levels are rejected.** Use `"INFO"`, not `"info"`.
- **`capture_caller_info` adds overhead.** Disable in tight loops.
- **All `setup_logging` arguments are keyword-only.** Positional calls are a `TypeError`.

## API Reference

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `setup_logging(**options)` | `Logger` | Configure and register a logger |
| `get_logger(name="")` | `Logger` | Get a logger by name (inherits root config) |
| `reset_logging()` | `None` | Close all handlers, clear the registry |
| `remove_logger(name)` | `bool` | Remove and close a single logger |

### Classes

| Class | Description |
|-------|-------------|
| `LogFormatter` | Configurable formatter covering all output styles |
| `CleanFileHandler` | File handler with automatic ANSI stripping |

### Constants

| Constant | Description |
|----------|-------------|
| `DEFAULT_LOG_COLORS` | Default color scheme for each level |
| `__version__` | Package version string |

## Examples

See the [`examples/`](./examples) directory for runnable scripts:

```bash
python examples/basic.py              # default colored output
python examples/box_styles.py         # all box styles
python examples/custom_colors.py      # custom color scheme
python examples/extra_fields.py       # structured data
python examples/file_logging.py       # console + file output
python examples/level_filtering.py    # level thresholds
python examples/named_loggers.py      # named logger hierarchy
python examples/plain_output.py       # no colors
python examples/custom_date_format.py
python examples/demo.py               # full feature walkthrough
```

## For AI coding assistants

See [`AGENTS.md`](./AGENTS.md) for canonical imports, antipatterns, and the full color-string grammar tailored for code-generating AI tools.

## License

[MIT](./LICENSE)
