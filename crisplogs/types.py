"""
Public type aliases for crisplogs.

These aliases narrow the accepted values for the configuration arguments
of :func:`crisplogs.setup_logging` and :class:`crisplogs.LogFormatter`.
Importing them from the package root lets users annotate their own code
with the same types crisplogs uses internally::

    from crisplogs import Level, Style, ExtraFormat, Width, LogColors

    def configure(level: Level = "INFO", style: Style | None = None) -> None:
        ...
"""

from __future__ import annotations

from typing import Literal, TypedDict, Union

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
"""Valid log-level strings. Always uppercase."""

Style = Literal["short-fixed", "short-dynamic", "long-boxed"]
"""Valid box styles. ``None`` (no box) is handled as ``Optional[Style]``."""

ExtraFormat = Literal["inline", "json", "pretty"]
"""How structured ``extra={...}`` data is rendered alongside the message."""

Width = Union[int, Literal["auto"]]
"""Box width: a positive integer in characters, or ``"auto"`` to size to content."""


class LogColors(TypedDict, total=False):
    """Per-level color overrides accepted by ``setup_logging(log_colors=...)``.

    All keys are optional; missing levels fall back to the defaults in
    :data:`crisplogs.DEFAULT_LOG_COLORS`. Each value follows the
    ``[modifier_]color[,bg_color]`` mini-grammar (see ``log_colors``
    docstring on :func:`crisplogs.setup_logging`).
    """

    DEBUG: str
    INFO: str
    WARNING: str
    ERROR: str
    CRITICAL: str


__all__ = ["Level", "Style", "ExtraFormat", "Width", "LogColors"]
