import numpy as np
import pandas
import yaml
import zipfile

from io import BytesIO, StringIO


PIXELSET_EXPORT_META_FILENAME = 'meta.yaml'
PIXELSET_EXPORT_PIXELS_FILENAME = 'pixels.csv'


def export_pixelsets(pixel_sets):
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
    zipfile.ZipFile
        A ZipFile archive.

    """

    pixelsets_meta = {}

    omics_unit_col = 'Omics Unit'
    df = pandas.DataFrame(columns=(omics_unit_col,))

    for index, pixel_set in enumerate(pixel_sets):
        pixel_set_id = pixel_set.get_short_uuid()

        # add metadata for this pixel set
        pixelsets_meta[pixel_set_id] = {
            'pixelset': pixel_set_id,
            'description': pixel_set.description,
            'columns': [(index * 2) + 1, (index * 2) + 2],
        }

        value_col = f'Value {pixel_set_id}'
        score_col = f'QS {pixel_set_id}'

        # add new columns for the current pixel set
        df = df.assign(**{value_col: np.NaN, score_col: np.NaN, })

        for pixel in pixel_set.pixels.all():
            omics_unit = pixel.omics_unit.reference.identifier

            if not (df[omics_unit_col] == omics_unit).any():
                # we create an empty row for this new omics unit
                df = df.append({omics_unit_col: omics_unit}, ignore_index=True)

            df.loc[
                df[omics_unit_col] == omics_unit, value_col
            ] = pixel.value
            df.loc[
                df[omics_unit_col] == omics_unit, score_col
            ] = pixel.quality_score

    # create in-memory archive
    archive = zipfile.ZipFile(
        BytesIO(),
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

    return archive
