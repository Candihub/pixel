import pandas
import re

from django.utils.translation import ugettext as _

from .export import get_dataframe_and_meta_for_pixelsets


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

    df, __ = get_dataframe_and_meta_for_pixelsets(
        pixel_set_ids,
        omics_units=omics_units,
        with_links=True,
    )

    html = df.to_html(
        escape=False,
        max_rows=display_limit,
    ).replace(' border="1"', '')  # pandas hardcodes table borders...

    # replace the empty table body with a message.
    if len(df.index) == 0:
        html = re.sub(
            r'<tbody>\s*\n\s*</tbody>',
            (
                '<tbody>'
                '<tr class="empty"><td colspan="{}">{}</td></tr>'
                '</tbody>'
            ).format(
                len(df.columns)+1,
                _("Your selection gave no results"),
            ),
            html
        )

    return html
