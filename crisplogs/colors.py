"""
ANSI color code mapping and parsing.

Supports the same color strings as Python's ``colorlog``:
basic colors, bold/dim modifiers, background colors, and
comma-separated combinations like ``"bold_red,bg_white"``.
"""

from __future__ import annotations

from typing import Dict

FG_COLORS: Dict[str, int] = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "purple": 35,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
}

BG_COLORS: Dict[str, int] = {
    "black": 40,
    "red": 41,
    "green": 42,
    "yellow": 43,
    "blue": 44,
    "purple": 45,
    "magenta": 45,
    "cyan": 46,
    "white": 47,
}

MODIFIERS: Dict[str, int] = {
    "bold": 1,
    "thin": 2,
    "dim": 2,
    "italic": 3,
    "underline": 4,
}

RESET = "\x1b[0m"


def parse_color_string(color_str: str) -> str:
    """
    Parse a colorlog-compatible color string into an ANSI escape sequence.

    Examples::

        >>> parse_color_string("red")
        '\\x1b[31m'
        >>> parse_color_string("bold_red")
        '\\x1b[1;31m'
        >>> parse_color_string("bold_red,bg_white")
        '\\x1b[1;31;47m'
    """
    parts = color_str.split(",")
    codes: list[int] = []

    for part in parts:
        trimmed = part.strip().lower()

        if trimmed == "reset":
            return RESET

        if trimmed.startswith("bg_"):
            color = trimmed[3:]
            if color in BG_COLORS:
                codes.append(BG_COLORS[color])
        elif "_" in trimmed:
            idx = trimmed.index("_")
            modifier = trimmed[:idx]
            color = trimmed[idx + 1 :]
            if modifier in MODIFIERS:
                codes.append(MODIFIERS[modifier])
            if color in FG_COLORS:
                codes.append(FG_COLORS[color])
        elif trimmed in MODIFIERS:
            codes.append(MODIFIERS[trimmed])
        elif trimmed in FG_COLORS:
            codes.append(FG_COLORS[trimmed])

    return f"\x1b[{';'.join(str(c) for c in codes)}m" if codes else ""


DEFAULT_LOG_COLORS: Dict[str, str] = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}
