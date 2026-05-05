"""
Formatter for crisplogs.

A single :class:`LogFormatter` class covers all output styles via options,
replacing the previous separate formatter classes.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from .colors import RESET, parse_color_string
from .exceptions import InvalidExtraFormatError, InvalidWidthError
from .types import ExtraFormat, Width
from .utils import strip_ansi, word_wrap

_VALID_EXTRA_FORMATS = ("inline", "json", "pretty")

# Box-drawing characters as constants so f-string expressions stay backslash-free
# (backslashes in f-string expressions are a SyntaxError on Python 3.8-3.11).
_TL = "\u250c"  # top-left
_TR = "\u2510"  # top-right
_BL = "\u2514"  # bottom-left
_BR = "\u2518"  # bottom-right
_H = "\u2500"   # horizontal
_V = "\u2502"   # vertical


class LogFormatter(logging.Formatter):
    """Single configurable log formatter covering all crisplogs output styles.

    Most users should call :func:`crisplogs.setup_logging` instead and let
    it construct a ``LogFormatter`` for them. Use this class directly only
    when integrating with custom handlers.

    The four canonical configurations are:

    +--------------------------+--------------------------------------------------+
    | Style                    | Options                                          |
    +==========================+==================================================+
    | Colored (no box)         | ``box=False``                                    |
    +--------------------------+--------------------------------------------------+
    | Short fixed box          | ``box=True, width=N``                            |
    +--------------------------+--------------------------------------------------+
    | Short dynamic box        | ``box=True, full_border=True, width="auto"``     |
    +--------------------------+--------------------------------------------------+
    | Long boxed               | ``box=True, word_wrap=True, width=N``            |
    +--------------------------+--------------------------------------------------+

    Args:
        log_colors: Mapping of level names (``"DEBUG"`` ... ``"CRITICAL"``)
            to color strings following the ``[modifier_]color[,bg_color]``
            grammar (see :func:`crisplogs.setup_logging` for the full
            grammar and examples).
        colored: Apply ANSI colors. Default ``True``.
        extra_format: How ``extra={...}`` fields are rendered:
            ``"inline"``, ``"json"``, or ``"pretty"``. Default ``"inline"``.
        box: Draw a box around each entry. Default ``False``.
        full_border: With ``box=True``, draw the right border (and
            corners) too. Default ``False`` (left-border only).
        width: Box width in characters, or ``"auto"`` to size to the
            longest line. Default ``100``.
        word_wrap: Word-wrap long lines within the box. Default ``False``.
        datefmt: ``strftime``-style date format. Default
            ``"%Y-%m-%d %H:%M:%S"``.

    Raises:
        InvalidExtraFormatError: If ``extra_format`` is not one of
            ``"inline"``, ``"json"``, ``"pretty"``.
        InvalidWidthError: If ``width`` is not a positive int or
            ``"auto"``.

    Note:
        ``LogFormatter`` is not a supported subclassing point. Configure
        behavior via constructor options instead.

    Example:
        >>> from crisplogs import LogFormatter
        >>> fmt = LogFormatter(
        ...     log_colors={"INFO": "bold_green"},
        ...     colored=True,
        ...     box=True,
        ...     full_border=True,
        ...     width="auto",
        ... )
    """

    def __init__(
        self,
        *,
        log_colors: Dict[str, str],
        colored: bool = True,
        extra_format: ExtraFormat = "inline",
        box: bool = False,
        full_border: bool = False,
        width: Width = 100,
        word_wrap: bool = False,
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        if extra_format not in _VALID_EXTRA_FORMATS:
            raise InvalidExtraFormatError(
                f"extra_format must be one of "
                f"{', '.join(repr(s) for s in _VALID_EXTRA_FORMATS)}; "
                f"got {extra_format!r}"
            )
        if width != "auto" and (
            not isinstance(width, int) or isinstance(width, bool) or width <= 0
        ):
            raise InvalidWidthError(
                f"width must be a positive int or 'auto'; got {width!r}"
            )

        super().__init__(datefmt=datefmt)
        self._log_colors = log_colors
        self._colored = colored
        self._extra_format: ExtraFormat = extra_format
        self._box = box
        self._full_border = full_border
        self._width: Width = width
        self._word_wrap = word_wrap

    def __repr__(self) -> str:
        return (
            f"LogFormatter(colored={self._colored!r}, box={self._box!r}, "
            f"full_border={self._full_border!r}, width={self._width!r}, "
            f"word_wrap={self._word_wrap!r}, extra_format={self._extra_format!r}, "
            f"datefmt={self.datefmt!r})"
        )

    @staticmethod
    def _safe_stringify(obj: Any, indent: Optional[int] = None) -> str:
        try:
            return json.dumps(obj, indent=indent, default=str)
        except (TypeError, ValueError):
            return "[Circular]"

    def _serialize_extra(self, extra: Optional[Dict[str, Any]]) -> str:
        if not extra:
            return ""

        fmt = self._extra_format

        if fmt == "json":
            return f" {self._safe_stringify(extra)}"

        if fmt == "pretty":
            return f"\n{self._safe_stringify(extra, indent=2)}"

        parts: list[str] = []
        for k, v in extra.items():
            if v is None or isinstance(v, (str, int, float, bool)):
                parts.append(f"{k}={v}")
            else:
                parts.append(f"{k}={self._safe_stringify(v)}")
        return " [" + " ".join(parts) + "]"

    @staticmethod
    def _pad_visual(text: str, width: int) -> str:
        return text + " " * max(0, width - len(strip_ansi(text)))

    def _format_base(self, record: logging.LogRecord) -> str:
        """Build the base line (no box, no extras)."""
        timestamp = self.formatTime(record, self.datefmt)
        level_name = record.levelname.ljust(8)
        name = record.name or "root"
        pathname = record.pathname
        lineno = record.lineno
        message = record.getMessage()

        if self._colored:
            lc = parse_color_string(self._log_colors.get(record.levelname, "white"))
            blue = parse_color_string("blue")
            cyan = parse_color_string("cyan")
            mc = parse_color_string(self._log_colors.get(record.levelname, "white"))

            return (
                f"{lc}{level_name}{RESET} "
                f"{timestamp} "
                f"{blue}[{name}]{RESET} "
                f"{cyan}{pathname}:{lineno}{RESET} - "
                f"{mc}{message}{RESET}"
            )

        return (
            f"{level_name} {timestamp} "
            f"[{name}] "
            f"{pathname}:{lineno} - "
            f"{message}"
        )

    _RESERVED: frozenset = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "message",
        "asctime", "taskName",
    })

    def _extract_extra(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in self._RESERVED
        }
        return extras if extras else None

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)

        message = self._format_base(record)

        extra = self._extract_extra(record)
        if not self._box or self._word_wrap:
            message += self._serialize_extra(extra)

        if not self._box:
            return message

        lines = message.split("\n")

        if self._width == "auto":
            w = max((len(strip_ansi(line)) for line in lines), default=0)
        else:
            w = int(self._width)

        if self._word_wrap:
            wrapped: list[str] = []
            for line in lines:
                wrapped.extend(word_wrap(line, w))
            content_lines = wrapped
        else:
            content_lines = lines

        if self._full_border:
            top = _TL + _H * (w + 2) + _TR
            bottom = _BL + _H * (w + 2) + _BR
            rows = [f"{_V} {self._pad_visual(line, w)} {_V}" for line in content_lines]
            return "\n".join([top, *rows, bottom])

        top = _TL + _H * (w + 2)
        bottom = _BL + _H * (w + 2)
        if self._word_wrap:
            rows = [f"{_V} {line}" for line in content_lines]
        else:
            rows = [f"{_V} {self._pad_visual(line, w)} " for line in content_lines]
        return "\n".join([top, *rows, bottom])
