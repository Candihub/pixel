import pytest

from io import StringIO

from django.core.management import call_command


def test_for_missing_migrations(db):
    """Look for missing migrations

    Hat tip to David Winterbottom:
    http://tech.octopus.energy/news/2016/01/21/testing-for-missing-migrations-in-django.html
    """
    output = StringIO()
    try:
        call_command(
            'makemigrations',
            interactive=False,
            dry_run=True,
            exit_code=True,
            stdout=output
        )
    except SystemExit as e:
        # The exit code will be 1 when there are no missing migrations
        assert str(e) == '1'
    else:  # pragma: no cover
        pytest.fail(
            "There are missing migrations:\n{}".format(output.getvalue())
        )
