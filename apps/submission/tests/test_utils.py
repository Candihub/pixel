import pytest

from ..utils import is_hidden_task


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
