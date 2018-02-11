from django.test import TestCase

from ..templatetags import explorer


class HighlightTestCase(TestCase):

    def test_highlight_returns_text_when_empty_word(self):

        expected = 'foo bar baz'
        assert explorer.highlight('foo bar baz', '') == expected

    def test_highlight(self):

        expected = '<span class="highlight">foo</span> bar baz'
        assert explorer.highlight('foo bar baz', 'foo') == expected

    def test_highlight_matches_all_occurences(self):

        expected = (
            '<span class="highlight">foo</span> bar baz'
            ' nope <span class="highlight">foo</span> bar baz'
        )
        assert explorer.highlight(
            'foo bar baz nope foo bar baz',
            'foo'
        ) == expected

    def test_highlight_matches_part_of_words(self):

        expected = 'l<span class="highlight">ooo</span>oong word'
        assert explorer.highlight('looooong word', 'ooo') == expected


class ConcatTestCase(TestCase):

    def test_concat(self):

        expected = 'foo-bar'
        assert explorer.concat('foo-', 'bar') == expected
