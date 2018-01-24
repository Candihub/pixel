import numpy as np
import pandas
import yaml
import zipfile

from io import BytesIO, StringIO


def export_pixelsets(pixel_sets):
    pixelsets_meta = {}

    omics_unit_col = 'Omics Unit'
    df = pandas.DataFrame(columns=(omics_unit_col,))

    for index, pixel_set in enumerate(pixel_sets):
        pixel_set_id = pixel_set.get_short_uuid()

        # add metadata for this pixel set
        pixelsets_meta[pixel_set_id] = {
            'pixelset': pixel_set_id,
            'description': pixel_set.description,
            'columns': [index * 2 + 1, index * 2 + 2],
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
        'meta.yaml',
        yaml.dump({'pixelsets': list(pixelsets_meta.values())})
    )

    csv = StringIO()
    df.to_csv(
        path_or_buf=csv,
        na_rep='NA',
        float_format='%.2f',
        index=False,
    )

    # add `pixels.csv` file
    archive.writestr('pixels.csv', csv.getvalue())

    return archive
