

def get_omics_units_from_session(session, default=[]):

    return session.get(
        'explorer', {}
    ).get(
        'omics_units', default
    )


def get_selected_pixel_sets_from_session(session, default=[]):

    return session.get(
        'explorer', {}
    ).get(
        'pixel_sets', default
    )


def set_omics_units_to_session(session, omics_units=[]):

    explorer = session.get('explorer', {})
    explorer.update({'omics_units': omics_units})

    session['explorer'] = explorer


def set_selected_pixel_sets_to_session(session, pixel_sets=[]):

    explorer = session.get('explorer', {})
    explorer.update({'pixel_sets': pixel_sets})

    session['explorer'] = explorer
