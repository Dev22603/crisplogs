"""Tests for crisplogs.colors — ANSI color parsing."""

from __future__ import annotations

import pytest

from crisplogs.colors import RESET, parse_color_string


class TestParseColorString:
    def test_basic_colors(self):
        assert parse_color_string("red") == "\x1b[31m"
        assert parse_color_string("green") == "\x1b[32m"
        assert parse_color_string("cyan") == "\x1b[36m"
        assert parse_color_string("blue") == "\x1b[34m"
        assert parse_color_string("yellow") == "\x1b[33m"
        assert parse_color_string("white") == "\x1b[37m"

    def test_bold_modifier(self):
        assert parse_color_string("bold_red") == "\x1b[1;31m"
        assert parse_color_string("bold_green") == "\x1b[1;32m"

    def test_dim_thin_modifier(self):
        assert parse_color_string("thin_white") == "\x1b[2;37m"
        assert parse_color_string("dim_white") == "\x1b[2;37m"

    def test_italic_modifier(self):
        assert parse_color_string("italic_cyan") == "\x1b[3;36m"

    def test_background_colors(self):
        assert parse_color_string("bg_red") == "\x1b[41m"
        assert parse_color_string("bg_white") == "\x1b[47m"
        assert parse_color_string("bg_black") == "\x1b[40m"

    def test_combined_bold_fg_bg(self):
        assert parse_color_string("bold_red,bg_white") == "\x1b[1;31;47m"

    def test_reset(self):
        assert parse_color_string("reset") == RESET

    def test_unknown_returns_empty(self):
        assert parse_color_string("nonexistent") == ""

    def test_modifier_only(self):
        assert parse_color_string("bold") == "\x1b[1m"

    def test_magenta_alias(self):
        # magenta and purple share the same code
        assert parse_color_string("magenta") == parse_color_string("purple")

    def test_whitespace_in_combo(self):
        # spaces around comma should be tolerated
        result = parse_color_string("bold_red , bg_white")
        assert result == "\x1b[1;31;47m"
