import pytest

from pathlib import Path
from tempfile import gettempdir

from django.conf import settings

from ..utils import ensure_tree, is_hidden_task


def test_is_hidden_task():

    assert is_hidden_task('start') is True
    assert is_hidden_task('end') is True
    assert is_hidden_task('check') is True
    assert is_hidden_task('check_download') is True
    assert is_hidden_task('check_foo') is True
    assert is_hidden_task('foo') is False
    assert is_hidden_task('bar') is False
    assert is_hidden_task('baz') is False
    with pytest.raises(ValueError):
        is_hidden_task(None)
    with pytest.raises(ValueError):
        is_hidden_task(23)
    with pytest.raises(ValueError):
        is_hidden_task(['foo', ])
    with pytest.raises(ValueError):
        is_hidden_task(('foo', ))


def test_ensure_tree():

    relative_path = Path('foo/bar/baz.txt')

    expected = Path(settings.MEDIA_ROOT) / relative_path
    assert ensure_tree(relative_path, dry_run=True) == expected

    root = gettempdir()
    expected = Path(root) / relative_path
    assert ensure_tree(relative_path, root=root, dry_run=True) == expected

    assert expected.parent.exists() is False
    assert ensure_tree(relative_path, root=root) == expected
    assert expected.parent.exists() is True
