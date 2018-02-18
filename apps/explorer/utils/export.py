import pandas
import re
import uuid
import yaml
import zipfile

from io import BytesIO, StringIO
from django.utils.translation import ugettext as _

from apps.core.models import Pixel


PIXELSET_EXPORT_META_FILENAME = 'meta.yaml'
PIXELSET_EXPORT_PIXELS_FILENAME = 'pixels.csv'


def _get_pixelsets_dataframe_and_metadata(pixel_set_ids,
                                          omics_units=None,
                                          descriptions=dict(),
                                          with_links=False):
    """The function takes Pixel Set IDs and optionally a list of Omics Units, a
    hash map of Pixel Set descriptions, and a boolean to determine whether to
    build URLs for omics units. This function returns a pandas.DataFrame and a
    hash map containing metadata related to the Pixel Sets.

    The list of Omics Units should contain identifiers and will be used to
    filter the pixels.

    Parameters
    ----------

    pixel_set_ids: list
        A list of Pixel Set ids.
    omics_units: list
        A list of Omics Units ids.
    descriptions: dict
        A hash map containing Pixel Set descriptions indexed by ID.
    with_links: bool
        Whether the omics units should have URLs or not.

    Returns
    -------
    df: pandas.DataFrame
        A pandas DataFrame.
    meta: dict
        A hash map indexed by Pixel Set ID. Values are dict with information
        for each Pixel Set.
    """

    columns = ['Omics Unit', 'Description']
    indexes = set()
    meta = dict()
    pixels = dict()

    # we build a dict with the pixel information for each omics unit, and we
    # compute the list of indexes and columns to construct the pandas dataframe
    # after. It is better to prepare these information than to dynamically
    # build the dataframe.
    for index, pixel_set_id in enumerate(pixel_set_ids):
        if not isinstance(pixel_set_id, uuid.UUID):
            short_id = uuid.UUID(pixel_set_id).hex[:7]
        else:
            short_id = pixel_set_id.hex[:7]

        value_col = f'Value {short_id}'
        score_col = f'QS {short_id}'

        # add columns for this pixel set
        columns.append(value_col)
        columns.append(score_col)

        # add metadata for this pixel set
        meta[short_id] = {
            'columns': [(index * 2) + 1, (index * 2) + 2],
            'pixelset': short_id,
            'description': descriptions.get(pixel_set_id, ''),
        }

        if short_id not in pixels:
            pixels[short_id] = []

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

            description = pixel.omics_unit.reference.description
            link = '<a href="{}">{}</a>'.format(
                pixel.omics_unit.reference.url,
                omics_unit,
            )

            pixels[short_id].append({
                'description': description.replace('\n', ' '),
                'link': link,
                'omics_unit': omics_unit,
                'quality_score': pixel.quality_score,
                'value': pixel.value,
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
                    pixel['link'] if with_links else pixel['omics_unit'],
                    pixel['description'],
                    pixel['value'],
                    pixel['quality_score'],
                ]
        # drop the indexes to get numerical indexes instead of omics units (so
        # that we have numbers displayed in the HTML table)
        df = df.reset_index(drop=True)

    return df, meta


def export_pixelsets(pixel_sets, omics_units=[]):
    """This function exports a list of PixelSet objects as a ZIP archive.

    The (in-memory) ZIP archive contains a `meta.yaml` file and a `pixels.csv`
    file according to this spec: https://github.com/Candihub/pixel/issues/144.

    Parameters
    ----------
    pixel_sets : iterable
        A sequence, an iterator, or some other object which supports iteration,
        containing PixelSet objects.

    Returns
    -------
    io.BytesIO
        A Binary I/O containing the ZIP archive.

    """

    descriptions = {}
    for pixel_set in pixel_sets:
        descriptions[pixel_set.id] = pixel_set.description

    df, pixelsets_meta = _get_pixelsets_dataframe_and_metadata(
        pixel_set_ids=descriptions.keys(),
        omics_units=omics_units,
        descriptions=descriptions,
    )

    stream = BytesIO()
    archive = zipfile.ZipFile(
        stream,
        mode='w',
        compression=zipfile.ZIP_DEFLATED
    )

    # add `meta.yaml` file
    archive.writestr(
        PIXELSET_EXPORT_META_FILENAME,
        yaml.dump({'pixelsets': list(pixelsets_meta.values())})
    )

    csv = StringIO()
    df.to_csv(
        path_or_buf=csv,
        na_rep='NA',
        index=False,
    )

    # add `pixels.csv` file
    archive.writestr(PIXELSET_EXPORT_PIXELS_FILENAME, csv.getvalue())

    archive.close()

    return stream


def export_pixels(pixel_set, omics_units=[], output=None):
    """This function exports the Pixels of a given PixelSet as a CSV file.

    If the list of `omics_units` is empty, all Pixels will be exported.

    Parameters
    ----------
    pixel_set : apps.core.models.PixelSet
        A PixelSet object.
    omics_units: list, optional
        A list of omics unit identifiers to export.
    output : String or File handler, optional
        A string or file handler to write the CSV content.

    Returns
    -------
    io.StringIO
        A String I/O containing the CSV file if `output` is not specified,
        `output` otherwise.

    """

    qs = pixel_set.pixels.select_related('omics_unit__reference')

    # we only filter by Omics Units when specified.
    if len(omics_units) > 0:
        qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

    data = list(
        qs.values_list(
            'omics_unit__reference__identifier',
            'value',
            'quality_score',
        )
    )

    df = pandas.DataFrame(data, columns=('Omics Unit', 'Value', 'QS', ))

    if output is None:
        output = StringIO()

    df.to_csv(
        path_or_buf=output,
        na_rep='NA',
        index=False,
    )

    return output


def export_pixelsets_as_html(pixel_set_ids,
                             omics_units=None,
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

    df, __ = _get_pixelsets_dataframe_and_metadata(
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
