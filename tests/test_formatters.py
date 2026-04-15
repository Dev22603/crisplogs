"""Tests for crisplogs.formatters — LogFormatter."""

from __future__ import annotations

import pytest

from crisplogs.formatters import LogFormatter

from .conftest import make_record

BASE = dict(
    log_colors={"INFO": "green", "ERROR": "red", "WARNING": "yellow",
                "DEBUG": "cyan", "CRITICAL": "bold_red"},
    colored=False,
    datefmt="%H:%M:%S",
)


class TestPlainOutput:
    def test_contains_level_and_message(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record())
        assert "INFO" in out
        assert "Test message" in out

    def test_no_ansi_codes(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record())
        assert "\x1b[" not in out

    def test_colored_output_has_ansi(self):
        fmt = LogFormatter(**{**BASE, "colored": True})
        out = fmt.format(make_record())
        assert "\x1b[" in out
        assert "INFO" in out
        assert "Test message" in out

    def test_contains_name_and_path(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record())
        assert "[test]" in out
        assert "/app/main.py" in out
        assert "25" in out


class TestExtraFields:
    def test_inline_extra(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record(extra={"user_id": 42}))
        assert "[user_id=42]" in out

    def test_inline_multiple_extras(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record(extra={"a": 1, "b": "hello"}))
        assert "a=1" in out
        assert "b=hello" in out

    def test_json_extra(self):
        fmt = LogFormatter(**{**BASE, "extra_format": "json"})
        out = fmt.format(make_record(extra={"user_id": 42}))
        assert '{"user_id": 42}' in out

    def test_pretty_extra(self):
        fmt = LogFormatter(**{**BASE, "extra_format": "pretty"})
        out = fmt.format(make_record(extra={"user_id": 42}))
        assert '"user_id": 42' in out

    def test_nested_object_inline(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record(extra={"config": {"port": 3000}}))
        assert 'config={"port": 3000}' in out
        assert "[object" not in out

    def test_circular_reference_inline(self):
        fmt = LogFormatter(**BASE)
        d: dict = {"a": 1}
        d["self"] = d
        out = fmt.format(make_record(extra=d))
        # Should not raise; circular is handled
        assert "a=1" in out

    def test_circular_reference_json(self):
        fmt = LogFormatter(**{**BASE, "extra_format": "json"})
        d: dict = {"a": 1}
        d["self"] = d
        out = fmt.format(make_record(extra=d))
        assert "[Circular]" in out

    def test_no_extra_no_brackets(self):
        fmt = LogFormatter(**BASE)
        out = fmt.format(make_record())
        assert "[" not in out.split("-", 1)[-1].split("]", 1)[-1]


class TestShortFixedBox:
    def test_left_border_structure(self):
        fmt = LogFormatter(**{**BASE, "box": True, "width": 80})
        lines = fmt.format(make_record()).split("\n")
        assert lines[0].startswith("┌")
        assert lines[1].startswith("│ ")
        assert lines[-1].startswith("└")

    def test_no_right_corner(self):
        fmt = LogFormatter(**{**BASE, "box": True, "width": 80})
        lines = fmt.format(make_record()).split("\n")
        assert not lines[0].endswith("┐")
        assert not lines[-1].endswith("┘")

    def test_extra_ignored(self):
        # short-fixed box does NOT append extras
        fmt = LogFormatter(**{**BASE, "box": True, "width": 80})
        out = fmt.format(make_record(extra={"user_id": 42}))
        assert "user_id" not in out


class TestShortDynamicBox:
    def test_full_border_structure(self):
        fmt = LogFormatter(**{**BASE, "box": True, "full_border": True, "width": "auto"})
        lines = fmt.format(make_record()).split("\n")
        assert lines[0].startswith("┌") and lines[0].endswith("┐")
        assert lines[1].startswith("│ ") and lines[1].endswith(" │")
        assert lines[-1].startswith("└") and lines[-1].endswith("┘")

    def test_auto_width_fits_content(self):
        fmt = LogFormatter(**{**BASE, "box": True, "full_border": True, "width": "auto"})
        lines = fmt.format(make_record()).split("\n")
        # top and bottom should have same length
        assert len(lines[0]) == len(lines[-1])


class TestLongBoxedFormatter:
    def test_left_border_structure(self):
        fmt = LogFormatter(**{**BASE, "box": True, "word_wrap": True, "width": 80})
        lines = fmt.format(make_record()).split("\n")
        assert lines[0].startswith("┌")
        assert lines[1].startswith("│ ")
        assert lines[-1].startswith("└")

    def test_word_wraps_long_message(self):
        fmt = LogFormatter(**{**BASE, "box": True, "word_wrap": True, "width": 40})
        long_msg = "This is a very long message that should definitely wrap across multiple lines"
        out = fmt.format(make_record(message=long_msg))
        content_lines = [l for l in out.split("\n") if l.startswith("│")]
        assert len(content_lines) > 1

    def test_extra_appended(self):
        fmt = LogFormatter(**{**BASE, "box": True, "word_wrap": True, "width": 200})
        out = fmt.format(make_record(extra={"user_id": 42, "action": "login"}))
        assert "user_id=42" in out
        assert "action=login" in out
