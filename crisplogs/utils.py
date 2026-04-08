"""
Internal utilities for crisplogs.

Provides helper functions used across the package.
"""

import re

# Regex to match ANSI escape sequences (colors, cursor moves, etc.)
_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """
    Remove all ANSI escape sequences from a string.

    Used to produce clean plain-text output for file handlers,
    since color codes are not readable in log files.

    Args:
        text: String potentially containing ANSI escape codes.

    Returns:
        The input string with all ANSI codes removed.

    Example::

        >>> strip_ansi("\\x1b[32mHello\\x1b[0m")
        'Hello'
    """
    return _ANSI_ESCAPE.sub("", text)
