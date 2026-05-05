"""
crisplogs - Beautiful, colored, and boxed logging for Python.

Quickstart::

    from crisplogs import setup_logging

    logger = setup_logging()  # colored logs, no box, DEBUG level
    logger.info("Hello from crisplogs!")

With a box style::

    setup_logging(colored=True, style="long-boxed")

With file logging (ANSI codes auto-stripped)::

    setup_logging(file="app.log", file_level="WARNING")

Named loggers::

    setup_logging()
    child = get_logger("myapp.db")  # inherits root handlers
"""

from __future__ import annotations

import logging
import sys
from typing import Dict, Optional

from .colors import DEFAULT_LOG_COLORS
from .exceptions import (
    CrisplogsError,
    InvalidColorError,
    InvalidExtraFormatError,
    InvalidLevelError,
    InvalidStyleError,
    InvalidWidthError,
)
from .formatters import LogFormatter
from .handlers import CleanFileHandler
from .types import ExtraFormat, Level, LogColors, Style, Width

__version__ = "0.3.0"

__all__ = [
    "CleanFileHandler",
    "CrisplogsError",
    "DEFAULT_LOG_COLORS",
    "ExtraFormat",
    "InvalidColorError",
    "InvalidExtraFormatError",
    "InvalidLevelError",
    "InvalidStyleError",
    "InvalidWidthError",
    "Level",
    "LogColors",
    "LogFormatter",
    "Style",
    "Width",
    "__version__",
    "get_logger",
    "remove_logger",
    "reset_logging",
    "setup_logging",
]

_LEVEL_VALUES: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_VALID_STYLES = ("short-fixed", "short-dynamic", "long-boxed")
_VALID_EXTRA_FORMATS = ("inline", "json", "pretty")

DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

_loggers: Dict[str, logging.Logger] = {}


class _FastLogger(logging.Logger):
    """Logger that optionally skips expensive caller-info stack-frame capture."""


def _no_caller_info(self: logging.Logger, stack_info: bool = False, stacklevel: int = 1):
    return "<unknown>", 0, "<unknown>", None


def setup_logging(
    *,
    colored: bool = True,
    style: Optional[Style] = None,
    level: Level = "DEBUG",
    width: Width = 100,
    datefmt: str = DEFAULT_DATEFMT,
    log_colors: Optional[LogColors] = None,
    file: Optional[str] = None,
    file_level: Optional[Level] = None,
    name: str = "",
    extra_format: ExtraFormat = "inline",
    capture_caller_info: bool = True,
) -> logging.Logger:
    """Configure a logger with colors and optional box formatting in one call.

    This is the main entry point for crisplogs. Call it once at application
    startup. All arguments are keyword-only.

    Args:
        colored: Enable colored console output. Default ``True``.
        style: Box style for console output. One of ``"short-fixed"``,
            ``"short-dynamic"``, ``"long-boxed"``, or ``None`` (no box).
            Default ``None``.
        level: Minimum log level for the console handler. Must be one of
            ``"DEBUG"``, ``"INFO"``, ``"WARNING"``, ``"ERROR"``,
            ``"CRITICAL"`` (uppercase). Default ``"DEBUG"``.
        width: Box width in characters, or the string ``"auto"`` to size
            to content. Used by ``"short-fixed"`` and ``"long-boxed"``.
            Default ``100``.
        datefmt: ``strftime``-style date format. Default
            ``"%Y-%m-%d %H:%M:%S"``.
        log_colors: Override default colors for specific levels. Values
            follow the grammar ``[modifier_]color[,bg_color]``:

            - ``modifier`` is one of ``bold_``, ``thin_``, ``dim_``,
              ``italic_``, ``underline_``.
            - ``color`` is one of ``black``, ``red``, ``green``,
              ``yellow``, ``blue``, ``purple``/``magenta``, ``cyan``,
              ``white``.
            - ``bg`` follows ``bg_<color>`` using the same color names.

            Valid examples: ``"green"``, ``"bold_red"``,
            ``"bold_white,bg_red"``. Invalid: ``"GREEN"`` (case),
            ``"bright_red"`` (unknown modifier).
        file: Path to a log file. ANSI codes are stripped automatically.
            Default ``None`` (no file output).
        file_level: Minimum level for file output. Defaults to ``level``.
        name: Logger name. ``""`` configures the root logger. Default
            ``""``.
        extra_format: How ``extra={...}`` fields are rendered:
            ``"inline"`` (``[k=v k2=v2]``), ``"json"`` (compact JSON),
            ``"pretty"`` (indented JSON). Default ``"inline"``.
        capture_caller_info: Capture caller file/line on each log call.
            Disable in hot paths; logs will show ``<unknown>:0``.
            Default ``True``.

    Returns:
        The configured :class:`logging.Logger` instance.

    Raises:
        InvalidLevelError: If ``level`` or ``file_level`` is not a valid
            log level.
        InvalidStyleError: If ``style`` is not a valid style.
        InvalidWidthError: If ``width`` is not a positive int or
            ``"auto"``.
        InvalidExtraFormatError: If ``extra_format`` is not one of
            ``"inline"``, ``"json"``, ``"pretty"``.

    Example:
        >>> from crisplogs import setup_logging
        >>> logger = setup_logging(level="INFO", style="long-boxed")
        >>> logger.info("Server started", extra={"port": 8000})
    """
    if level not in _LEVEL_VALUES:
        raise InvalidLevelError(
            f"level must be one of {', '.join(repr(k) for k in _LEVEL_VALUES)}; "
            f"got {level!r}"
        )
    if file_level is not None and file_level not in _LEVEL_VALUES:
        raise InvalidLevelError(
            f"file_level must be one of {', '.join(repr(k) for k in _LEVEL_VALUES)} "
            f"or None; got {file_level!r}"
        )
    if style is not None and style not in _VALID_STYLES:
        raise InvalidStyleError(
            f"style must be one of {', '.join(repr(s) for s in _VALID_STYLES)} "
            f"or None; got {style!r}"
        )
    if extra_format not in _VALID_EXTRA_FORMATS:
        raise InvalidExtraFormatError(
            f"extra_format must be one of "
            f"{', '.join(repr(s) for s in _VALID_EXTRA_FORMATS)}; "
            f"got {extra_format!r}"
        )
    if width != "auto" and (not isinstance(width, int) or isinstance(width, bool) or width <= 0):
        raise InvalidWidthError(
            f"width must be a positive int or 'auto'; got {width!r}"
        )
    if file is not None and (not isinstance(file, str) or not file):
        raise CrisplogsError("file must be a non-empty string or None")

    colors = {**DEFAULT_LOG_COLORS, **(log_colors or {})}

    fmt_kwargs: Dict[str, object] = dict(
        log_colors=colors,
        colored=colored,
        extra_format=extra_format,
        datefmt=datefmt,
    )

    style_to_opts: Dict[Optional[str], Dict[str, object]] = {
        None: dict(box=False),
        "short-fixed": dict(box=True, width=width),
        "short-dynamic": dict(box=True, full_border=True, width="auto"),
        "long-boxed": dict(box=True, word_wrap=True, width=width),
    }
    fmt_kwargs.update(style_to_opts[style])

    if not colored and style is not None:
        fmt_kwargs["log_colors"] = {k: "white" for k in colors}
        fmt_kwargs["colored"] = False

    formatter = LogFormatter(**fmt_kwargs)  # type: ignore[arg-type]

    if name in _loggers:
        _loggers[name].handlers.clear()

    prev_class = logging.getLoggerClass()
    logging.setLoggerClass(_FastLogger)
    logger = logging.getLogger(name)
    logging.setLoggerClass(prev_class)

    if not isinstance(logger, _FastLogger):
        logger.__class__ = _FastLogger  # type: ignore[assignment]

    if not capture_caller_info:
        import types
        logger.findCaller = types.MethodType(_no_caller_info, logger)  # type: ignore[method-assign]

    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(_LEVEL_VALUES[level])
    logger.addHandler(console_handler)

    if file is not None:
        resolved_file_level = file_level or level
        file_handler = CleanFileHandler(file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(_LEVEL_VALUES[resolved_file_level])
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger


def get_logger(name: str = "") -> logging.Logger:
    """Retrieve a configured logger or create one inheriting root handlers.

    :func:`setup_logging` should be called first; otherwise the returned
    logger inherits Python's default (unconfigured) ``logging`` setup
    and will emit no output until configured.

    Args:
        name: Logger name. ``""`` returns the root logger.

    Returns:
        The :class:`logging.Logger` instance. Named child loggers
        inherit the root handlers, so messages appear with the child's
        name in the output (e.g. ``[db]``).

    Example:
        >>> from crisplogs import setup_logging, get_logger
        >>> setup_logging(level="INFO")
        >>> db = get_logger("db")
        >>> db.info("connected")
    """
    if name in _loggers:
        return _loggers[name]

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

    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger


def reset_logging() -> None:
    """Tear down all crisplogs-managed loggers.

    Closes every handler, clears the registry, and is safe to call
    repeatedly. Use this in test teardowns to avoid handler leaks
    between tests, or before re-running :func:`setup_logging` with
    different options at runtime.

    Example:
        >>> from crisplogs import reset_logging, setup_logging
        >>> reset_logging()
        >>> setup_logging(level="WARNING")  # fresh config
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
    """Remove and close a single logger from the registry.

    Args:
        name: Logger name to remove.

    Returns:
        ``True`` if a logger with that name was registered and removed,
        ``False`` if no such logger exists.

    Example:
        >>> from crisplogs import setup_logging, remove_logger
        >>> setup_logging(name="db")
        >>> remove_logger("db")
        True
        >>> remove_logger("db")
        False
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
