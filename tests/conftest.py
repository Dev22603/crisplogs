"""Shared test fixtures for crisplogs tests."""

from __future__ import annotations

import logging
from datetime import datetime

import pytest

from crisplogs import reset_logging


@pytest.fixture(autouse=True)
def clean_registry():
    """Reset the crisplogs logger registry before and after each test."""
    reset_logging()
    yield
    reset_logging()


def make_record(
    message: str = "Test message",
    level: str = "INFO",
    name: str = "test",
    pathname: str = "/app/main.py",
    lineno: int = 25,
    extra: dict | None = None,
) -> logging.LogRecord:
    """Create a LogRecord for formatter tests."""
    record = logging.LogRecord(
        name=name,
        level=getattr(logging, level),
        pathname=pathname,
        lineno=lineno,
        msg=message,
        args=(),
        exc_info=None,
    )
    record.created = datetime(2025, 9, 8, 12, 30, 45).timestamp()
    # Freeze asctime so tests are deterministic.
    record.asctime = "2025-09-08 12:30:45"
    if extra:
        for k, v in extra.items():
            setattr(record, k, v)
    return record
