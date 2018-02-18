from apps.explorer.views.helpers import (
    get_search_terms_from_session, get_selected_pixel_sets_from_session,
    set_search_terms_to_session, set_selected_pixel_sets_to_session,
)


def test_get_search_terms_from_session_returns_empty_list():

    empty_session = dict()

    search_terms = get_search_terms_from_session(empty_session, key='foo')
    assert search_terms == []


def test_get_search_terms_from_session_returns_default_if_supplied():

    empty_session = dict()
    default = 'some-default-value'

    search_terms = get_search_terms_from_session(
        empty_session,
        key='foo',
        default=default
    )
    assert search_terms == default


def test_get_selected_pixel_sets_from_session_returns_empty_list():

    empty_session = dict()

    selected_pixel_sets = get_selected_pixel_sets_from_session(empty_session)
    assert selected_pixel_sets == []


def test_get_selected_pixel_sets_from_session_returns_default_if_supplied():

    empty_session = dict()
    default = 'some-default-value'

    selected_pixel_sets = get_selected_pixel_sets_from_session(
        empty_session,
        default=default
    )
    assert selected_pixel_sets == default


def test_set_search_terms_to_session():

    session = dict()
    search_terms = ['bar']

    set_search_terms_to_session(
        session,
        key='foo',
        search_terms=search_terms
    )
    assert 'explorer' in session
    assert 'foo' in session['explorer']
    assert session['explorer']['foo'] == search_terms


def test_set_search_terms_to_session_preserves_other_values():

    session = dict()

    # create a default session, without anything inside
    set_search_terms_to_session(session, key='something-else')
    assert 'explorer' in session
    assert 'something-else' in session['explorer']

    # set omics units now
    search_terms = ['bar']

    set_search_terms_to_session(
        session,
        key='foo',
        search_terms=search_terms
    )
    assert 'explorer' in session
    assert 'foo' in session['explorer']
    assert 'something-else' in session['explorer']
    assert session['explorer']['foo'] == search_terms


def test_set_selected_pixel_sets_to_session():

    session = dict()
    pixel_sets = ['bar']

    set_selected_pixel_sets_to_session(
        session,
        pixel_sets=pixel_sets
    )
    assert 'explorer' in session
    assert 'pixel_sets' in session['explorer']
    assert session['explorer']['pixel_sets'] == pixel_sets


def test_set_selected_pixel_sets_to_session_preserves_other_values():

    session = dict()

    # create a default session, without anything inside
    set_search_terms_to_session(session, key='something-else')
    assert 'explorer' in session
    assert 'something-else' in session['explorer']

    # set pixel sets now
    pixel_sets = ['bar']

    set_selected_pixel_sets_to_session(
        session,
        pixel_sets=pixel_sets
    )
    assert 'explorer' in session
    assert 'pixel_sets' in session['explorer']
    assert 'something-else' in session['explorer']
    assert session['explorer']['pixel_sets'] == pixel_sets
