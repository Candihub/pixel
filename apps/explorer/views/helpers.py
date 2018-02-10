

def get_omics_units_from_session(session, default=[]):
    return session.get(
        'explorer', {}
    ).get(
        'pixels', {}
    ).get(
        'omics_units', default
    )


def get_selected_pixel_sets_from_session(session, default=[]):
    return session.get(
        'explorer', {}
    ).get(
        'pixelsets', default
    )
