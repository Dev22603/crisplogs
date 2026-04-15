"""
Formatter for crisplogs.

A single :class:`LogFormatter` class covers all output styles via options,
replacing the previous four separate formatter classes.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Literal, Optional, Union

from .colors import RESET, parse_color_string
from .utils import strip_ansi, word_wrap

ExtraFormat = Literal["inline", "json", "pretty"]


class LogFormatter(logging.Formatter):
    """
    Single configurable log formatter.

    Covers all output styles through constructor options:

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
        log_colors: Mapping of level names to colorlog-style color strings.
        colored: Whether to apply ANSI colors. Default ``True``.
        extra_format: How extra fields are rendered (``"inline"``,
            ``"json"``, ``"pretty"``). Default ``"inline"``.
        box: Draw a box around each log entry. Default ``False``.
        full_border: Use full border (top-right + bottom-right corners)
            instead of left-border only. Default ``False``.
        width: Box width in characters, or ``"auto"`` to size to the
            longest line. Default ``100``.
        word_wrap: Word-wrap long lines within the box. Default ``False``.
        datefmt: Date/time format string. Default ``"%Y-%m-%d %H:%M:%S"``.
    """

    def __init__(
        self,
        *,
        log_colors: Dict[str, str],
        colored: bool = True,
        extra_format: ExtraFormat = "inline",
        box: bool = False,
        full_border: bool = False,
        width: Union[int, str] = 100,
        word_wrap: bool = False,
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ) -> None:
        super().__init__(datefmt=datefmt)
        self._log_colors = log_colors
        self._colored = colored
        self._extra_format: ExtraFormat = extra_format
        self._box = box
        self._full_border = full_border
        self._width = width
        self._word_wrap = word_wrap

    # -- helpers ----------------------------------------------------------

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

        # inline: [key=value key2=value2]
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

    # -- core format ------------------------------------------------------

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

    # Built-in LogRecord attributes that should NOT be treated as extras.
    _RESERVED: frozenset[str] = frozenset({
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

    # -- public -----------------------------------------------------------

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        # Let the base class populate record.message and record.asctime.
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)

        message = self._format_base(record)

        # Extras are appended for plain output and word-wrapped boxes.
        extra = self._extract_extra(record)
        if not self._box or self._word_wrap:
            message += self._serialize_extra(extra)

        if not self._box:
            return message

        lines = message.split("\n")

        # Determine effective box width.
        if self._width == "auto":
            w = max((len(strip_ansi(line)) for line in lines), default=0)
        else:
            w = int(self._width)

        # Word-wrap if requested.
        if self._word_wrap:
            wrapped: list[str] = []
            for line in lines:
                wrapped.extend(word_wrap(line, w))
            content_lines = wrapped
        else:
            content_lines = lines

        if self._full_border:
            top = f"\u250c{'\u2500' * (w + 2)}\u2510"
            bottom = f"\u2514{'\u2500' * (w + 2)}\u2518"
            rows = [f"\u2502 {self._pad_visual(l, w)} \u2502" for l in content_lines]
            return "\n".join([top, *rows, bottom])

        # Left-border only.
        top = f"\u250c{'\u2500' * (w + 2)}"
        bottom = f"\u2514{'\u2500' * (w + 2)}"
        if self._word_wrap:
            rows = [f"\u2502 {l}" for l in content_lines]
        else:
            rows = [f"\u2502 {self._pad_visual(l, w)} " for l in content_lines]
        return "\n".join([top, *rows, bottom])
