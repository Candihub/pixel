

def get_search_terms_from_session(session, key, default=[]):

    return session.get(
        'explorer', {}
    ).get(
        key, default
    )


def get_selected_pixel_sets_from_session(session, default=[]):

    return session.get(
        'explorer', {}
    ).get(
        'pixel_sets', default
    )


def set_search_terms_to_session(session, key, search_terms=[]):

    explorer = session.get('explorer', {})
    explorer.update({key: search_terms})

    session['explorer'] = explorer


def set_selected_pixel_sets_to_session(session, pixel_sets=[]):

    explorer = session.get('explorer', {})
    explorer.update({'pixel_sets': pixel_sets})

    session['explorer'] = explorer
