"""Tests for setup_logging, get_logger, reset_logging, remove_logger."""

from __future__ import annotations

import logging

import pytest

from crisplogs import (
    get_logger,
    remove_logger,
    reset_logging,
    setup_logging,
)


class TestSetupLogging:
    def test_returns_logger(self):
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)

    def test_default_level_is_debug(self):
        logger = setup_logging()
        assert logger.level == logging.DEBUG

    def test_console_handler_level(self):
        logger = setup_logging(level="WARNING")
        assert logger.handlers[0].level == logging.WARNING

    def test_colored_true(self, capsys):
        logger = setup_logging(colored=True)
        logger.info("colorful")
        captured = capsys.readouterr()
        assert "\x1b[" in captured.out

    def test_colored_false(self, capsys):
        logger = setup_logging(colored=False)
        logger.info("plain")
        captured = capsys.readouterr()
        assert "\x1b[" not in captured.out

    def test_style_short_fixed(self, capsys):
        logger = setup_logging(style="short-fixed")
        logger.info("boxed")
        captured = capsys.readouterr()
        assert "┌" in captured.out
        assert "└" in captured.out

    def test_style_short_dynamic(self, capsys):
        logger = setup_logging(style="short-dynamic")
        logger.info("dynamic")
        captured = capsys.readouterr()
        assert "┌" in captured.out
        assert "┐" in captured.out

    def test_style_long_boxed(self, capsys):
        logger = setup_logging(style="long-boxed")
        logger.info("long boxed")
        captured = capsys.readouterr()
        assert "┌" in captured.out
        assert "└" in captured.out

    def test_level_filtering(self, capsys):
        logger = setup_logging(level="WARNING")
        logger.debug("should not appear")
        logger.info("should not appear")
        logger.warning("should appear")
        captured = capsys.readouterr()
        assert "should not appear" not in captured.out
        assert "should appear" in captured.out

    def test_named_logger(self):
        logger = setup_logging(name="myapp")
        assert logger.name == "myapp"

    def test_no_propagation(self):
        logger = setup_logging(name="myapp")
        assert logger.propagate is False

    def test_clears_previous_handlers(self, capsys):
        setup_logging(name="dup")
        setup_logging(name="dup")
        logger = logging.getLogger("dup")
        assert len(logger.handlers) == 1

    def test_extra_format_inline(self, capsys):
        logger = setup_logging(extra_format="inline")
        logger.info("msg", extra={"k": "v"})
        captured = capsys.readouterr()
        assert "[k=v]" in captured.out

    def test_extra_format_json(self, capsys):
        logger = setup_logging(extra_format="json")
        logger.info("msg", extra={"k": "v"})
        captured = capsys.readouterr()
        assert '{"k": "v"}' in captured.out

    def test_custom_log_colors(self, capsys):
        logger = setup_logging(colored=True, log_colors={"INFO": "bold_green"})
        logger.info("bold green")
        captured = capsys.readouterr()
        # bold_green = \x1b[1;32m
        assert "\x1b[1;32m" in captured.out


class TestValidation:
    def test_invalid_level_raises(self):
        with pytest.raises(TypeError, match="Invalid log level"):
            setup_logging(level="VERBOSE")  # type: ignore

    def test_invalid_file_level_raises(self):
        with pytest.raises(TypeError, match="Invalid file_level"):
            setup_logging(file_level="VERBOSE")  # type: ignore

    def test_invalid_width_raises(self):
        with pytest.raises(TypeError, match="Invalid width"):
            setup_logging(width=0)

    def test_negative_width_raises(self):
        with pytest.raises(TypeError, match="Invalid width"):
            setup_logging(width=-1)

    def test_empty_file_path_raises(self):
        with pytest.raises(TypeError, match="Invalid file path"):
            setup_logging(file="")


class TestGetLogger:
    def test_returns_same_logger(self):
        setup_logging(name="app")
        logger = get_logger("app")
        assert logger.name == "app"

    def test_inherits_root_handlers(self):
        root = setup_logging()  # root logger
        child = get_logger("child")
        assert len(child.handlers) == len(root.handlers)

    def test_bare_logger_when_no_root(self):
        logger = get_logger("orphan")
        assert isinstance(logger, logging.Logger)

    def test_get_root_logger(self):
        root = setup_logging()
        retrieved = get_logger("")
        assert retrieved is root


class TestResetLogging:
    def test_clears_registry(self):
        setup_logging(name="app1")
        setup_logging(name="app2")
        reset_logging()
        # After reset, get_logger returns a fresh bare logger
        logger = get_logger("app1")
        assert len(logger.handlers) == 0

    def test_handlers_cleared(self):
        logger = setup_logging(name="app")
        reset_logging()
        assert len(logger.handlers) == 0


class TestRemoveLogger:
    def test_removes_existing_logger(self):
        setup_logging(name="todelete")
        result = remove_logger("todelete")
        assert result is True

    def test_returns_false_for_missing(self):
        result = remove_logger("nonexistent")
        assert result is False

    def test_handlers_cleared_on_remove(self):
        logger = setup_logging(name="todelete2")
        remove_logger("todelete2")
        assert len(logger.handlers) == 0
