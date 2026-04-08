"""
Custom log handlers for crisplogs.

Provides handlers that produce clean output for non-terminal destinations.
"""

import logging
from typing import Any

from .utils import strip_ansi


class CleanFileHandler(logging.FileHandler):
    """
    A file handler that automatically strips ANSI color codes from log output.

    Logs written to files should be plain text for readability in editors,
    log aggregators, and CI systems. This handler wraps the standard
    ``logging.FileHandler`` and removes all ANSI escape sequences before writing.

    Args:
        filename: Path to the log file (e.g. ``"app.log"``).
        mode: File open mode. Defaults to ``"a"`` (append).
        encoding: File encoding. Defaults to ``"utf-8"``.
        *args: Passed to ``logging.FileHandler``.
        **kwargs: Passed to ``logging.FileHandler``.

    Example::

        handler = CleanFileHandler("app.log")
        handler.setFormatter(some_formatter)
        logger.addHandler(handler)
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
