import pandas
import re
import uuid

from django.utils.translation import ugettext as _

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

    columns = ['Omics Unit', 'Description']
    indexes = set()
    pixels = dict()

    # we build a dict with the pixel information for each omics unit, and we
    # compute the list of indexes and columns to construct the pandas dataframe
    # after. It is better to prepare these information than to dynamically
    # build the dataframe.
    for index, pixel_set_id in enumerate(pixel_set_ids):
        if not isinstance(pixel_set_id, uuid.UUID):
            pixel_set_id = uuid.UUID(pixel_set_id)

        short_id = pixel_set_id.hex[:7]

        value_col = f'Value {short_id}'
        score_col = f'QS {short_id}'

        columns.append(value_col)
        columns.append(score_col)

        qs = Pixel.objects.filter(
            pixel_set_id=pixel_set_id
        ).select_related(
            'omics_unit__reference'
        ).order_by(
            'omics_unit__reference__identifier'
        )

        for pixel in qs:
            omics_unit = pixel.omics_unit.reference.identifier

            # filter by omics_units if supplied
            if omics_units and omics_unit not in omics_units:
                continue

            if short_id not in pixels:
                pixels[short_id] = []

            description = pixel.omics_unit.reference.description
            link = '<a href="{}">{}</a>'.format(
                pixel.omics_unit.reference.url,
                omics_unit,
            )

            pixels[short_id].append({
                'omics_unit': omics_unit,
                'link': link,
                'description': description.replace('\n', ' '),
                'value': pixel.value,
                'quality_score': pixel.quality_score,
            })
            indexes.add(omics_unit)

    df = pandas.DataFrame(index=sorted(indexes), columns=columns)

    if indexes:
        # populate the dataframe with each pixel information
        for short_id in pixels.keys():
            for pixel in pixels[short_id]:
                df.loc[
                    pixel['omics_unit'],
                    [
                        'Omics Unit',
                        'Description',
                        f'Value {short_id}',
                        f'QS {short_id}',
                    ]
                ] = [
                    pixel['link'],
                    pixel['description'],
                    pixel['value'],
                    pixel['quality_score'],
                ]
        # drop the indexes to get numerical indexes instead of omics units (so
        # that we have numbers displayed in the HTML table)
        df = df.reset_index(drop=True)

    html = df.to_html(
        escape=False,
        max_rows=display_limit,
    ).replace(' border="1"', '')  # pandas hardcodes table borders...

    # replace the empty table body with a message.
    if not indexes:
        html = re.sub(
            r'<tbody>\s*\n\s*</tbody>',
            (
                '<tbody>'
                '<tr class="empty"><td colspan="{}">{}</td></tr>'
                '</tbody>'
            ).format(
                len(columns)+1,
                _("Your selection gave no results"),
            ),
            html
        )

    return html
