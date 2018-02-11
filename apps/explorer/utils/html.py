import numpy as np
import pandas
import uuid

from apps.core.models import Pixel


def create_html_table_for_pixelsets(pixel_set_ids, omics_units=None,
                                    display_limit=None):
    """This function creates a HTML table displaying the pixels related to the
    set of Pixel Sets given as first argument.

    The function takes Pixel Set IDs, and optionally a list of Omics Units and
    a number of rows to render in the HTML table.

    The list of Omics Units should contain identifiers and will be used to
    filter the pixels.

    Parameters
    ----------

    pixel_set_ids: list
        A list of Pixel Set ids.
    omics_units: list
        A list of Omics Units ids.
    display_limit: int
        The number of rows to render in the HTML table.

    Returns
    -------
    str
        A string containing the HTML table (not escaped).
    """

    # tell pandas not to truncate strings
    pandas.set_option('display.max_colwidth', -1)
    # tell pandas not to format floats
    pandas.set_option('display.float_format', lambda val: '{}'.format(val))

    omics_unit_col = 'ID'
    description_col = 'Description'
    omics_unit_link_col = 'Omics Unit'
    df = pandas.DataFrame(
        columns=(omics_unit_col, omics_unit_link_col, description_col,)
    )

    for index, pixel_set_id in enumerate(pixel_set_ids):
        if not isinstance(pixel_set_id, uuid.UUID):
            pixel_set_id = uuid.UUID(pixel_set_id)

        short_id = pixel_set_id.hex[:7]

        value_col = f'Value {short_id}'
        score_col = f'QS {short_id}'

        # add new columns for the current pixel set
        df = df.assign(**{value_col: np.NaN, score_col: np.NaN, })

        qs = Pixel.objects.filter(
            pixel_set_id=pixel_set_id
        ).select_related(
            'omics_unit__reference'
        ).order_by(
            'omics_unit__reference__identifier'
        )

        for pixel in qs:
            omics_unit = pixel.omics_unit.reference.identifier
            description = pixel.omics_unit.reference.description
            url = pixel.omics_unit.reference.url

            # we filter by omics_units if supplied
            if omics_units and omics_unit not in omics_units:
                continue

            if not (df[omics_unit_col] == omics_unit).any():
                link = '<a href="{}">{}</a>'.format(url, omics_unit)

                # we create an empty row for this new omics unit
                df = df.append({
                    omics_unit_col: omics_unit,
                    omics_unit_link_col: link,
                    description_col: description.replace('\n', ' '),
                }, ignore_index=True)

            df.loc[
                df[omics_unit_col] == omics_unit, value_col
            ] = pixel.value
            df.loc[
                df[omics_unit_col] == omics_unit, score_col
            ] = pixel.quality_score

    # Do not display the `ID` column
    columns = list(df.columns)
    columns.remove(omics_unit_col)

    html = df.to_html(
        columns=columns,
        escape=False,
        max_rows=display_limit,
    ).replace(' border="1"', '')  # pandas hardcodes table borders...

    return html
