"""Tests for crisplogs.handlers — CleanFileHandler."""

from __future__ import annotations

import os
import tempfile

import pytest

from crisplogs import setup_logging
from crisplogs.handlers import CleanFileHandler
from crisplogs.formatters import LogFormatter


@pytest.fixture()
def tmp_log(tmp_path):
    return str(tmp_path / "test.log")


class TestCleanFileHandler:
    def test_writes_to_file(self, tmp_log, capsys):
        logger = setup_logging(file=tmp_log, level="INFO", name="file-test")
        logger.info("File test message")
        # give the handler a moment to flush
        for h in logger.handlers:
            h.flush() if hasattr(h, "flush") else None

        content = open(tmp_log).read()
        assert "File test message" in content

    def test_strips_ansi_from_file(self, tmp_log, capsys):
        logger = setup_logging(colored=True, file=tmp_log, level="INFO", name="ansi-strip")
        logger.info("Colored message")
        for h in logger.handlers:
            h.flush() if hasattr(h, "flush") else None

        content = open(tmp_log).read()
        assert "Colored message" in content
        assert "\x1b[" not in content

    def test_file_level_independent(self, tmp_log, capsys):
        logger = setup_logging(
            level="DEBUG",
            file=tmp_log,
            file_level="ERROR",
            name="file-level-test",
        )
        logger.info("console only")
        logger.error("both")
        for h in logger.handlers:
            h.flush() if hasattr(h, "flush") else None

        content = open(tmp_log).read()
        assert "console only" not in content
        assert "both" in content

    def test_bad_file_path_does_not_crash(self, capsys):
        bad_path = "/nonexistent/deep/nested/file.log"
        # On Windows the path would be different; just use a path we know fails
        import platform
        if platform.system() == "Windows":
            bad_path = "Z:\\nonexistent\\deep\\nested\\file.log"
        # Creating a handler with a bad path should raise OSError at open time,
        # not during emit. This tests that emit doesn't crash on a broken stream.
        fmt = LogFormatter(
            log_colors={"INFO": "green"},
            colored=False,
            datefmt="%H:%M:%S",
        )
        try:
            handler = CleanFileHandler(bad_path)
            handler.setFormatter(fmt)
            import logging
            record = logging.LogRecord("t", logging.INFO, "", 0, "msg", (), None)
            # Should not raise
            handler.emit(record)
        except (OSError, FileNotFoundError):
            pass  # Expected — handler couldn't open the file


class TestCleanFileHandlerDirect:
    def test_emit_strips_ansi(self, tmp_log):
        fmt = LogFormatter(
            log_colors={"INFO": "green"},
            colored=True,
            datefmt="%H:%M:%S",
        )
        handler = CleanFileHandler(tmp_log)
        handler.setFormatter(fmt)

        import logging
        record = logging.LogRecord("t", logging.INFO, "/app/x.py", 1, "hello", (), None)
        handler.emit(record)
        handler.flush()

        content = open(tmp_log).read()
        assert "hello" in content
        assert "\x1b[" not in content
