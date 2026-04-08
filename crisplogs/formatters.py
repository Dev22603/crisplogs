"""
Formatter classes for crisplogs.

Provides colored and boxed log formatters built on top of ``colorlog.ColoredFormatter``.

Classes:
    ColoredLogFormatter: Colored log output with no box.
    ShortFixedBoxFormatter: Fixed-width box with left border only.
    ShortDynamicBoxFormatter: Dynamic-width box with full border (left + right).
    LongBoxedFormatter: Word-wrapped box with left border, ideal for long messages.
"""

import textwrap
from typing import Any

from colorlog import ColoredFormatter


class ColoredLogFormatter(ColoredFormatter):
    """
    A simple colored log formatter with no box decoration.

    Extends ``colorlog.ColoredFormatter`` without any visual wrapping.
    Each log level gets its own color for easy scanning.

    Example output::

        INFO     2025-09-08 12:30:45 [main] /app/main.py:25 - Server started
        ERROR    2025-09-08 12:31:12 [db] /app/db.py:45 - Connection failed
    """

    pass


class ShortFixedBoxFormatter(ColoredFormatter):
    """
    Wraps each log message inside a fixed-width box with left border only.

    Best suited for short, single-line log messages where you want
    visual separation between entries.

    Args:
        width: Box width in characters. Defaults to 100.
        *args: Passed to ``colorlog.ColoredFormatter``.
        **kwargs: Passed to ``colorlog.ColoredFormatter``.

    Example output::

        +--------------------------------------
        | INFO     2025-09-08 12:30:45 [main] - Server started
        +--------------------------------------
    """

    def __init__(self, *args: Any, width: int = 100, **kwargs: Any) -> None:
        self._box_width = width
        super().__init__(*args, **kwargs)

    def format(self, record: Any) -> str:
        message = super().format(record)
        lines = message.splitlines()

        width = self._box_width
        top = "\u250c" + "\u2500" * (width + 2)
        bottom = "\u2514" + "\u2500" * (width + 2)
        boxed = [top] + [f"\u2502 {line.ljust(width)} " for line in lines] + [bottom]

        return "\n".join(boxed)


class ShortDynamicBoxFormatter(ColoredFormatter):
    """
    Wraps each log message inside a dynamically sized full box (left + right borders).

    The box width adjusts automatically based on the longest line in the message.
    Best suited for short messages where you want a clean, tight border.

    Example output::

        +--------------------------------------------+
        | INFO     2025-09-08 12:30:45 - Server started |
        +--------------------------------------------+
    """

    def format(self, record: Any) -> str:
        message = super().format(record)
        lines = message.splitlines()

        width = max(len(line) for line in lines) if lines else 0
        top = "\u250c" + "\u2500" * (width + 2) + "\u2510"
        bottom = "\u2514" + "\u2500" * (width + 2) + "\u2518"
        boxed = [top] + [f"\u2502 {line.ljust(width)} \u2502" for line in lines] + [bottom]

        return "\n".join(boxed)


class LongBoxedFormatter(ColoredFormatter):
    """
    Wraps log messages inside a left-border box with intelligent word wrapping.

    Long lines are wrapped at word boundaries using Python's ``textwrap`` module,
    so words are never split mid-way. Any custom ``extra`` fields passed in the
    log call are automatically appended to the message.

    Best suited for verbose logs like API responses, error traces, or messages
    with extra context fields.

    Args:
        width: Maximum line width before wrapping. Defaults to 100.
        *args: Passed to ``colorlog.ColoredFormatter``.
        **kwargs: Passed to ``colorlog.ColoredFormatter``.

    Example output::

        +--------------------------------------
        | INFO     2025-09-08 12:34:56 [main] - This is a long message that wraps
        | neatly across multiple lines without breaking words. [user_id=42]
        +--------------------------------------
    """

    # Built-in log record attributes that should not be treated as extras.
    _RESERVED = {
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "message",
        "asctime", "taskName",
    }

    def __init__(self, *args: Any, width: int = 100, **kwargs: Any) -> None:
        self._box_width = width
        super().__init__(*args, **kwargs)

    def format(self, record: Any) -> str:
        message = super().format(record)

        # Detect and append custom extras
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in self._RESERVED
        }
        if extras:
            extras_str = " ".join(f"{k}={v}" for k, v in extras.items())
            message = f"{message} [{extras_str}]"

        # Word-wrap long lines
        lines = message.splitlines()
        width = self._box_width
        wrapped: list[str] = []
        for line in lines:
            wrapped.extend(
                textwrap.wrap(
                    line,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                or [""]  # preserve blank lines
            )

        top = "\u250c" + "\u2500" * (width + 2)
        bottom = "\u2514" + "\u2500" * (width + 2)
        boxed = [top] + [f"\u2502 {l}" for l in wrapped] + [bottom]

        return "\n".join(boxed)
