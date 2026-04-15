"""Tests for crisplogs.utils — strip_ansi and word_wrap."""

from __future__ import annotations

from crisplogs.utils import strip_ansi, word_wrap


class TestStripAnsi:
    def test_removes_color_codes(self):
        assert strip_ansi("\x1b[32mHello\x1b[0m") == "Hello"

    def test_plain_text_unchanged(self):
        assert strip_ansi("Hello World") == "Hello World"

    def test_removes_multiple_codes(self):
        assert strip_ansi("\x1b[1;31mError\x1b[0m: \x1b[33mwarn\x1b[0m") == "Error: warn"

    def test_empty_string(self):
        assert strip_ansi("") == ""

    def test_csi_cursor_sequences(self):
        assert strip_ansi("\x1b[2J") == ""
        assert strip_ansi("before\x1b[2Jafter") == "beforeafter"

    def test_osc_sequences(self):
        assert strip_ansi("\x1b]8;;http://example.com\x07text\x1b]8;;\x07") == "text"

    def test_bold_reset(self):
        assert strip_ansi("\x1b[1mBold\x1b[0m") == "Bold"


class TestWordWrap:
    def test_short_text_unchanged(self):
        assert word_wrap("Short", 100) == ["Short"]

    def test_wraps_long_text(self):
        text = "This is a long message that should be wrapped at a specified width"
        result = word_wrap(text, 20)
        assert len(result) > 1
        # No line should exceed the visual width
        for line in result:
            assert len(strip_ansi(line)) <= 20

    def test_empty_string(self):
        assert word_wrap("", 100) == [""]

    def test_preserves_long_word(self):
        long_word = "superlongwordthatexceedswidth"
        result = word_wrap(long_word, 10)
        assert result == [long_word]

    def test_wraps_ansi_colored_text_correctly(self):
        # The ANSI codes should not count toward width
        colored = "\x1b[32mhello\x1b[0m world"
        result = word_wrap(colored, 6)
        # "hello" visible width=5, "world" visible width=5, total=11 > 6
        assert len(result) == 2

    def test_multiple_spaces_treated_as_separator(self):
        result = word_wrap("a b", 100)
        # split() merges multiple spaces
        assert result == ["a b"]
