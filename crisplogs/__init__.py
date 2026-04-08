"""
crisplogs - Beautiful, colored, and boxed logging for Python.

Quickstart::

    from crisplogs import setup_logging

    setup_logging()  # colored logs, no box, DEBUG level

    import logging
    logger = logging.getLogger("myapp")
    logger.info("Hello from crisplogs!")

With a box style::

    setup_logging(colored=True, style="long-boxed")

With file logging::

    setup_logging(file="app.log", file_level="WARNING")
"""

import logging
import sys
from typing import Literal, Optional

from .formatters import (
    ColoredLogFormatter,
    LongBoxedFormatter,
    ShortDynamicBoxFormatter,
    ShortFixedBoxFormatter,
)
from .handlers import CleanFileHandler

__version__ = "0.1.0"

__all__ = [
    "setup_logging",
    "ColoredLogFormatter",
    "ShortFixedBoxFormatter",
    "ShortDynamicBoxFormatter",
    "LongBoxedFormatter",
    "CleanFileHandler",
]

# Type aliases for IDE autocomplete (ctrl+space shows all valid options).
Style = Literal["short-fixed", "short-dynamic", "long-boxed"]
Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Default color scheme applied to each log level.
DEFAULT_LOG_COLORS: dict[str, str] = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

# Default format string used by all formatters.
DEFAULT_FORMAT = (
    "%(log_color)s%(levelname)-8s%(reset)s "
    "%(asctime)s "
    "%(blue)s[%(name)s]%(reset)s "
    "%(cyan)s%(pathname)s:%(lineno)d%(reset)s - "
    "%(message_log_color)s%(message)s%(reset)s"
)

# Default date format.
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    colored: bool = True,
    style: Optional[Style] = None,
    level: Level = "DEBUG",
    width: int = 100,
    datefmt: str = DEFAULT_DATEFMT,
    log_colors: Optional[dict[str, str]] = None,
    file: Optional[str] = None,
    file_level: Optional[Level] = None,
    name: str = "",
) -> logging.Logger:
    """
    Configure logging with colors and optional box formatting in one call.

    This is the main entry point for crisplogs. Call it once at application
    startup to configure the root (or named) logger.

    Args:
        colored:
            Enable colored output on the console. Set to ``False`` for
            plain text console output (useful in CI or piped environments).
            Defaults to ``True``.

        style:
            Box style for console output. Options:

            - ``None`` -- No box, just colored text (default).
            - ``"short-fixed"`` -- Fixed-width box (left border only).
            - ``"short-dynamic"`` -- Dynamic-width box (full border, left + right).
            - ``"long-boxed"`` -- Word-wrapped box (left border), best for long messages.

        level:
            Minimum log level for the console handler. One of
            ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``.
            Defaults to ``"DEBUG"``.

        width:
            Box width in characters. Only used when ``style`` is set to
            ``"short-fixed"`` or ``"long-boxed"``. Ignored otherwise.
            Defaults to ``100``.

        datefmt:
            Date/time format string (any valid ``strftime`` format).
            Defaults to ``"%Y-%m-%d %H:%M:%S"``.

        log_colors:
            Override the default color for each log level. Pass a dict mapping
            level names to ``colorlog`` color strings. Example::

                log_colors={"INFO": "bold_green", "ERROR": "bold_red,bg_white"}

            See `colorlog docs <https://github.com/borntyping/python-colorlog>`_
            for available colors. Defaults to the built-in color scheme.

        file:
            Path to a log file (e.g. ``"app.log"``). When set, logs are also
            written to this file with ANSI color codes stripped automatically.
            Defaults to ``None`` (no file logging).

        file_level:
            Minimum log level for the file handler. Allows you to keep verbose
            console output while only writing important messages to disk.
            Defaults to the same value as ``level`` if not specified.

        name:
            Logger name. Use ``""`` (empty string) for the root logger, or
            pass a dotted name like ``"myapp.db"`` for a specific logger.
            Defaults to ``""`` (root logger).

    Returns:
        The configured ``logging.Logger`` instance.

    Examples:

        **Minimal setup** -- colored console, DEBUG level::

            from crisplogs import setup_logging
            setup_logging()

        **Boxed logs** -- long-boxed style with wider width::

            setup_logging(style="long-boxed", width=120)

        **Production** -- no colors, WARNING+ to file::

            setup_logging(colored=False, level="INFO", file="app.log", file_level="WARNING")

        **Custom colors**::

            setup_logging(log_colors={"INFO": "bold_green", "WARNING": "bold_yellow"})
    """
    colors = {**DEFAULT_LOG_COLORS, **(log_colors or {})}
    secondary = {"message": colors.copy()}

    # Common kwargs for all colorlog-based formatters.
    fmt_kwargs: dict = {
        "fmt": DEFAULT_FORMAT,
        "datefmt": datefmt,
        "log_colors": colors,
        "secondary_log_colors": secondary,
        "style": "%",
    }

    # Pick the right formatter class based on colored + style.
    if colored and style is None:
        formatter = ColoredLogFormatter(**fmt_kwargs)

    elif colored and style == "short-fixed":
        formatter = ShortFixedBoxFormatter(**fmt_kwargs, width=width)

    elif colored and style == "short-dynamic":
        formatter = ShortDynamicBoxFormatter(**fmt_kwargs)

    elif colored and style == "long-boxed":
        formatter = LongBoxedFormatter(**fmt_kwargs, width=width)

    elif not colored and style is None:
        # Plain formatter, no colors, no box.
        formatter = logging.Formatter(
            fmt=(
                "%(levelname)-8s %(asctime)s [%(name)s] "
                "%(pathname)s:%(lineno)d - %(message)s"
            ),
            datefmt=datefmt,
        )

    elif not colored and style is not None:
        # Box style but no colors -- use the box formatter with a plain format string.
        # We still use the colorlog formatter but with reset colors.
        no_color = {k: "white" for k in colors}
        no_color_kwargs: dict = {
            "fmt": (
                "%(levelname)-8s %(asctime)s [%(name)s] "
                "%(pathname)s:%(lineno)d - %(message)s"
            ),
            "datefmt": datefmt,
            "log_colors": no_color,
            "secondary_log_colors": {"message": no_color},
            "style": "%",
        }
        style_map = {
            "short-fixed": ShortFixedBoxFormatter,
            "short-dynamic": ShortDynamicBoxFormatter,
            "long-boxed": LongBoxedFormatter,
        }
        cls = style_map[style]
        if style in ("short-fixed", "long-boxed"):
            formatter = cls(**no_color_kwargs, width=width)
        else:
            formatter = cls(**no_color_kwargs)
    else:
        # Fallback (should not happen with typed params).
        formatter = logging.Formatter(datefmt=datefmt)

    # -- Console handler --
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level))

    # -- Configure logger --
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Let handlers decide what to pass through.
    logger.handlers.clear()  # Remove any existing handlers to avoid duplicates.
    logger.addHandler(console_handler)

    # -- File handler (optional) --
    if file is not None:
        resolved_file_level = file_level or level
        file_handler = CleanFileHandler(file)
        # File gets the same formatter (ANSI is stripped in the handler).
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, resolved_file_level))
        logger.addHandler(file_handler)

    return logger
