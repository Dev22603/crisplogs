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

Named loggers::

    setup_logging()
    child = get_logger("myapp.db")  # inherits root handlers
"""

from __future__ import annotations

import logging
import sys
from typing import Dict, Literal, Optional

from .colors import DEFAULT_LOG_COLORS
from .formatters import ExtraFormat, LogFormatter
from .handlers import CleanFileHandler

__version__ = "0.2.0"

__all__ = [
    "setup_logging",
    "get_logger",
    "reset_logging",
    "remove_logger",
    "LogFormatter",
    "CleanFileHandler",
    "DEFAULT_LOG_COLORS",
    "ExtraFormat",
    "__version__",
]

Style = Literal["short-fixed", "short-dynamic", "long-boxed"]
Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_LEVEL_VALUES: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

# Global logger registry keyed by name.
_loggers: Dict[str, logging.Logger] = {}


class _FastLogger(logging.Logger):
    """Logger that optionally skips expensive caller-info stack-frame capture."""


def _no_caller_info(self: logging.Logger, stack_info: bool = False, stacklevel: int = 1):
    return "<unknown>", 0, "<unknown>", None


def setup_logging(
    colored: bool = True,
    style: Optional[Style] = None,
    level: Level = "DEBUG",
    width: int = 100,
    datefmt: str = DEFAULT_DATEFMT,
    log_colors: Optional[Dict[str, str]] = None,
    file: Optional[str] = None,
    file_level: Optional[Level] = None,
    name: str = "",
    extra_format: ExtraFormat = "inline",
    capture_caller_info: bool = True,
) -> logging.Logger:
    """
    Configure logging with colors and optional box formatting in one call.

    This is the main entry point for crisplogs. Call it once at application
    startup to configure the root (or named) logger.

    Args:
        colored:
            Enable colored output on the console. Set to ``False`` for plain
            text (useful in CI or piped environments). Default ``True``.

        style:
            Box style for console output. One of:

            - ``None`` -- No box, plain colored text (default).
            - ``"short-fixed"`` -- Fixed-width left-border box.
            - ``"short-dynamic"`` -- Auto-width full-border box.
            - ``"long-boxed"`` -- Word-wrapped left-border box.

        level:
            Minimum log level for the console handler. Default ``"DEBUG"``.

        width:
            Box width in characters. Only used for ``"short-fixed"`` and
            ``"long-boxed"``. Default ``100``.

        datefmt:
            Date/time format string (``strftime`` syntax). Default
            ``"%Y-%m-%d %H:%M:%S"``.

        log_colors:
            Override default colors for specific log levels. Example::

                log_colors={"INFO": "bold_green", "ERROR": "bold_red,bg_white"}

        file:
            Path to a log file. ANSI codes are stripped automatically.
            Default ``None``.

        file_level:
            Minimum log level for the file handler. Defaults to ``level``.

        name:
            Logger name. ``""`` configures the root logger. Default ``""``.

        extra_format:
            How ``extra`` fields are rendered. One of:

            - ``"inline"`` -- ``[key=value key2=value2]`` (default).
            - ``"json"`` -- compact JSON ``{"key": "value"}``.
            - ``"pretty"`` -- indented multi-line JSON.

        capture_caller_info:
            Capture the caller's file path and line number on each log call.
            Disable for higher throughput in performance-critical code.
            Default ``True``.

    Returns:
        The configured :class:`logging.Logger` instance.

    Raises:
        TypeError: If any argument has an invalid value.
    """
    # --- validation -------------------------------------------------------
    if level not in _LEVEL_VALUES:
        raise TypeError(
            f'Invalid log level: "{level}". '
            f'Expected one of: {", ".join(_LEVEL_VALUES)}'
        )
    if file_level is not None and file_level not in _LEVEL_VALUES:
        raise TypeError(
            f'Invalid file_level: "{file_level}". '
            f'Expected one of: {", ".join(_LEVEL_VALUES)}'
        )
    if not isinstance(width, int) or width <= 0:
        raise TypeError(f"Invalid width: {width}. Must be a positive integer.")
    if file is not None and (not isinstance(file, str) or not file):
        raise TypeError("Invalid file path: must be a non-empty string.")

    # --- formatter --------------------------------------------------------
    colors = {**DEFAULT_LOG_COLORS, **(log_colors or {})}

    fmt_kwargs = dict(
        log_colors=colors,
        colored=colored,
        extra_format=extra_format,
        datefmt=datefmt,
    )

    style_to_opts = {
        None: dict(box=False),
        "short-fixed": dict(box=True, width=width),
        "short-dynamic": dict(box=True, full_border=True, width="auto"),
        "long-boxed": dict(box=True, word_wrap=True, width=width),
    }
    fmt_kwargs.update(style_to_opts[style])

    if not colored and style is not None:
        # Box but no colors: override all level colors to plain white.
        fmt_kwargs["log_colors"] = {k: "white" for k in colors}
        fmt_kwargs["colored"] = False

    formatter = LogFormatter(**fmt_kwargs)

    # --- logger -----------------------------------------------------------
    # Clear any previous registration to avoid duplicate handlers.
    if name in _loggers:
        _loggers[name].handlers.clear()

    # Temporarily switch logger class so our subclass is created.
    prev_class = logging.getLoggerClass()
    logging.setLoggerClass(_FastLogger)
    logger = logging.getLogger(name)
    logging.setLoggerClass(prev_class)

    # If it was already instantiated as a plain Logger (e.g. root), cast attrs.
    if not isinstance(logger, _FastLogger):
        logger.__class__ = _FastLogger  # type: ignore[assignment]

    if not capture_caller_info:
        import types
        logger.findCaller = types.MethodType(_no_caller_info, logger)  # type: ignore[method-assign]

    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    # --- console handler --------------------------------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(_LEVEL_VALUES[level])
    logger.addHandler(console_handler)

    # --- file handler (optional) ------------------------------------------
    if file is not None:
        resolved_file_level = file_level or level
        file_handler = CleanFileHandler(file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(_LEVEL_VALUES[resolved_file_level])
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str = "") -> logging.Logger:
    """
    Retrieve a previously configured logger, or create one that inherits
    the root logger's handlers.

    Example::

        setup_logging()                    # configure root
        db = get_logger("myapp.db")        # inherits root handlers
        db.info("Connected")

    Args:
        name: Logger name. ``""`` returns the root logger.

    Returns:
        The :class:`logging.Logger` instance.
    """
    if name in _loggers:
        return _loggers[name]

    # Inherit from root logger if available.
    root = _loggers.get("")
    if root:
        child = logging.getLogger(name)
        child.setLevel(root.level)
        child.handlers.clear()
        child.propagate = False
        for handler in root.handlers:
            child.addHandler(handler)
        _loggers[name] = child
        return child

    # No root configured — return a bare logger (no output until configured).
    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger


def reset_logging() -> None:
    """
    Tear down all loggers, closing their handlers and clearing the registry.

    Useful in tests or when reconfiguring logging at runtime::

        reset_logging()
        setup_logging(level="WARNING")  # start fresh
    """
    for logger in _loggers.values():
        for handler in logger.handlers[:]:
            try:
                handler.close()
            except Exception:
                pass
        logger.handlers.clear()
    _loggers.clear()


def remove_logger(name: str) -> bool:
    """
    Remove a single logger from the registry by name.

    Args:
        name: Logger name to remove.

    Returns:
        ``True`` if the logger existed and was removed, ``False`` otherwise.
    """
    logger = _loggers.get(name)
    if logger is None:
        return False
    for handler in logger.handlers[:]:
        try:
            handler.close()
        except Exception:
            pass
    logger.handlers.clear()
    del _loggers[name]
    return True
