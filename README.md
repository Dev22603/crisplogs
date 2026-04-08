# crisplogs

Beautiful, colored, and boxed logging for Python. One function call to set up production-ready logs with colors, box decorations, and file output.

## Installation

```bash
pip install crisplogs
```

## Quickstart

```python
from crisplogs import setup_logging
import logging

setup_logging()

logger = logging.getLogger("myapp")
logger.debug("This is a debug message")
logger.info("Server started successfully")
logger.warning("Disk usage at 85%")
logger.error("Failed to connect to database")
logger.critical("System is shutting down")
```

## Styles

### Colored (default)

Plain colored output. Each log level gets its own color for easy scanning.

```python
setup_logging(colored=True)
```

```
INFO     2025-09-08 12:30:45 [myapp] /app/main.py:25 - Server started
ERROR    2025-09-08 12:31:12 [myapp] /app/db.py:45 - Connection failed
```

### Short Fixed Box

Fixed-width box with left border only. Good for short messages.

```python
setup_logging(style="short-fixed")
```

```
┌──────────────────────────────────────────────────────────────────────────────────
│ INFO     2025-09-08 12:30:45 [myapp] /app/main.py:25 - Server started
└──────────────────────────────────────────────────────────────────────────────────
```

### Short Dynamic Box

Dynamic-width box with full border. Width adjusts to fit the message.

```python
setup_logging(style="short-dynamic")
```

```
┌──────────────────────────────────────────────────────────────────┐
│ INFO     2025-09-08 12:30:45 [myapp] - Server started           │
└──────────────────────────────────────────────────────────────────┘
```

### Long Boxed

Word-wrapped box with left border. Best for long messages and extra fields.

```python
setup_logging(style="long-boxed")
```

```
┌──────────────────────────────────────────────────────────────────────────────────
│ INFO     2025-09-08 12:34:56 [main] - This is a long message that wraps neatly
│ across multiple lines without breaking words in half. [user_id=42 action=login]
└──────────────────────────────────────────────────────────────────────────────────
```

To pass extra fields:

```python
logger.info("User logged in", extra={"user_id": 42, "action": "login"})
```

## Options

### `colored` (bool, default: `True`)

Enable or disable colored console output. Set to `False` for CI, piped output, or plain terminals.

```python
setup_logging(colored=False)
```

### `style` (str or None, default: `None`)

Box style. One of `"short-fixed"`, `"short-dynamic"`, `"long-boxed"`, or `None` for no box.

You can combine `colored` and `style` independently:

```python
setup_logging(colored=True, style="long-boxed")   # colored + boxed
setup_logging(colored=False, style="short-fixed")  # plain + boxed
setup_logging(colored=True, style=None)             # colored, no box
setup_logging(colored=False, style=None)            # plain, no box
```

### `level` (str, default: `"DEBUG"`)

Minimum log level for console output. One of `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`.

```python
setup_logging(level="INFO")  # hides DEBUG messages on console
```

### `width` (int, default: `100`)

Box width in characters. Only applies to `"short-fixed"` and `"long-boxed"` styles.

```python
setup_logging(style="long-boxed", width=120)
```

### `datefmt` (str, default: `"%Y-%m-%d %H:%M:%S"`)

Date/time format using `strftime` syntax.

```python
setup_logging(datefmt="%H:%M:%S")       # short: 12:30:45
setup_logging(datefmt="%d/%m/%Y %H:%M") # European: 08/09/2025 12:30
```

### `log_colors` (dict, default: built-in scheme)

Override colors for specific log levels. Uses [colorlog color strings](https://github.com/borntyping/python-colorlog#colors).

```python
setup_logging(log_colors={
    "DEBUG": "thin_white",
    "INFO": "bold_green",
    "WARNING": "bold_yellow",
    "ERROR": "bold_red,bg_white",
    "CRITICAL": "bold_white,bg_red",
})
```

### `file` (str or None, default: `None`)

Path to a log file. ANSI color codes are automatically stripped so the file stays clean and readable.

```python
setup_logging(file="logs/app.log")
```

### `file_level` (str or None, default: same as `level`)

Separate minimum level for the file handler. Useful when you want verbose console output but only important messages in the file.

```python
setup_logging(level="DEBUG", file="app.log", file_level="WARNING")
# Console shows everything, file only gets WARNING and above.
```

### `name` (str, default: `""`)

Logger name. Empty string configures the root logger (affects all loggers). Pass a name for a specific logger.

```python
setup_logging(name="myapp")

logger = logging.getLogger("myapp")       # uses crisplogs config
other = logging.getLogger("third_party")   # unaffected
```

## Full Example

```python
from crisplogs import setup_logging
import logging

# Colored + boxed console, warnings+ to file
setup_logging(
    colored=True,
    style="long-boxed",
    level="DEBUG",
    width=110,
    datefmt="%H:%M:%S",
    file="app.log",
    file_level="WARNING",
)

logger = logging.getLogger("myapp")

logger.debug("Loading configuration...")
logger.info("Server started on port 8000")
logger.warning("Cache miss rate is high", extra={"rate": "45%"})
logger.error("Payment processing failed", extra={"order_id": 9912})
```

## License

MIT
