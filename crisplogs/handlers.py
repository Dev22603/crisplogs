"""
Custom log handlers for crisplogs.

Provides handlers that produce clean output for non-terminal destinations.
"""

import logging
from typing import Any

from .utils import strip_ansi


class CleanFileHandler(logging.FileHandler):
    """File handler that strips ANSI color codes before writing.

    Wraps :class:`logging.FileHandler` and removes every ANSI escape
    sequence from the formatted message, so the same logger can emit
    colored output to a console handler and clean text to a file
    handler simultaneously.

    Args:
        filename: Path to the log file.
        mode: File open mode. Default ``"a"`` (append).
        encoding: File encoding. Default ``"utf-8"``.
        *args: Forwarded to :class:`logging.FileHandler`.
        **kwargs: Forwarded to :class:`logging.FileHandler`.

    Example:
        >>> import logging
        >>> from crisplogs import CleanFileHandler, LogFormatter
        >>> handler = CleanFileHandler("app.log")
        >>> handler.setFormatter(LogFormatter(log_colors={}, colored=False))
        >>> logging.getLogger().addHandler(handler)
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        encoding: str = "utf-8",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(filename, mode=mode, encoding=encoding, *args, **kwargs)

    def __repr__(self) -> str:
        return (
            f"CleanFileHandler(filename={self.baseFilename!r}, "
            f"level={logging.getLevelName(self.level)!r})"
        )

    def emit(self, record: logging.LogRecord) -> None:
        """Format the record, strip ANSI codes, then write to file."""
        try:
            msg = self.format(record)
            msg = strip_ansi(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)
