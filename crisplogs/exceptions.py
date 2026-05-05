"""
Typed exception hierarchy for crisplogs.

Every exception inherits from both :class:`CrisplogsError` and the
built-in :class:`ValueError`, so existing code that catches
``ValueError`` keeps working while new code can target a specific
subclass for fine-grained handling::

    from crisplogs import CrisplogsError, InvalidLevelError, setup_logging

    try:
        setup_logging(level="info")  # wrong case
    except InvalidLevelError as e:
        ...
    except CrisplogsError as e:      # any crisplogs-raised error
        ...
"""

from __future__ import annotations


class CrisplogsError(Exception):
    """Base class for all crisplogs exceptions."""


class InvalidLevelError(CrisplogsError, ValueError):
    """Raised when an unrecognized log level is passed to ``setup_logging``."""


class InvalidStyleError(CrisplogsError, ValueError):
    """Raised when an unrecognized ``style`` value is passed."""


class InvalidColorError(CrisplogsError, ValueError):
    """Raised when a color string cannot be parsed."""


class InvalidExtraFormatError(CrisplogsError, ValueError):
    """Raised when an unrecognized ``extra_format`` value is passed."""


class InvalidWidthError(CrisplogsError, ValueError):
    """Raised when ``width`` is neither a positive int nor the string ``"auto"``."""


__all__ = [
    "CrisplogsError",
    "InvalidLevelError",
    "InvalidStyleError",
    "InvalidColorError",
    "InvalidExtraFormatError",
    "InvalidWidthError",
]
