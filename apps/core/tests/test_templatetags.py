from ..templatetags import files


def test_filename():

    path = 'foo/bar/lol.txt'
    expected = 'lol.txt'
    assert files.filename(path) == expected
