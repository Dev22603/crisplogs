"""
Internal utilities for crisplogs.

Provides helper functions used across the package.
"""

from __future__ import annotations

import re

# Regex matching ANSI escape sequences (SGR, CSI, OSC, etc.).
_ANSI_ESCAPE = re.compile(
    r"[\x1b\x9b][\[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><~]"
    r"|\x1b\].*?(?:\x1b\\|\x07)",
)


def strip_ansi(text: str) -> str:
    """
    Remove all ANSI escape sequences from a string.

    Example::

        >>> strip_ansi("\\x1b[32mHello\\x1b[0m")
        'Hello'
    """
    return _ANSI_ESCAPE.sub("", text)


def word_wrap(text: str, width: int) -> list[str]:
    """
    Word-wrap text at word boundaries.

    ANSI escape sequences are excluded from width calculations so colored
    text wraps at the correct visible column. Long words that exceed
    *width* are kept intact (never broken mid-word).

    Example::

        >>> word_wrap("short", 100)
        ['short']
    """
    if not text:
        return [""]

    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current_line = words[0]

    for word in words[1:]:
        vis_current = len(strip_ansi(current_line))
        vis_word = len(strip_ansi(word))
        if vis_current + 1 + vis_word <= width:
            current_line += f" {word}"
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines
