from django.test import TestCase

from apps.explorer.forms import str_to_set


class StrToSetTestCase(TestCase):

    def test_empty_input_returns_empty_set(self):

        result = str_to_set('')
        assert type(result) == set
        assert len(result) == 0

    def test_returns_set(self):

        result = str_to_set('abc')
        assert type(result) == set
        assert len(result) == 1
        assert 'abc' in result

    def test_split_on_comma(self):

        result = str_to_set('a,b,c')
        assert len(result) == 3
        assert 'a' in result
        assert 'b' in result
        assert 'c' in result

    def test_split_on_space(self):

        result = str_to_set('a b c')
        assert len(result) == 3
        assert 'a' in result
        assert 'b' in result
        assert 'c' in result

    def test_split_on_newline(self):

        result = str_to_set('a\nb\nc')
        assert len(result) == 3
        assert 'a' in result
        assert 'b' in result
        assert 'c' in result

    def test_split_on_mixed_separators(self):

        input = """a,b     c,d
        e
        f
        g   h  , i j
        """

        result = str_to_set(input)
        assert len(result) == 10
        assert 'a' in result
        assert 'b' in result
        assert 'c' in result
        assert 'd' in result
        assert 'e' in result
        assert 'f' in result
        assert 'g' in result
        assert 'h' in result
        assert 'i' in result
        assert 'j' in result

    def test_returns_no_duplicates(self):

        result = str_to_set('a a a')
        assert len(result) == 1
        assert 'a' in result
