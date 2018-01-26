import pandas
import pytest
import yaml
import zipfile

from apps.core import factories
from apps.core.models import PixelSet
from apps.core.tests import CoreFixturesTestCase

from ...utils import (
    PIXELSET_EXPORT_META_FILENAME, PIXELSET_EXPORT_PIXELS_FILENAME,
    export_pixelsets, export_pixels,
)


class ExportPixelSetsTestCase(CoreFixturesTestCase):

    def _export_pixelsets(self, pixel_sets):

        stream = export_pixelsets(pixel_sets)
        return zipfile.ZipFile(stream, mode='r')

    def _assert_archive_is_valid(self, zip_archive):

        assert len(zip_archive.namelist()) == 2
        assert PIXELSET_EXPORT_META_FILENAME in zip_archive.namelist()
        assert PIXELSET_EXPORT_PIXELS_FILENAME in zip_archive.namelist()

    def test_export_without_pixelsets(self):

        zip_archive = self._export_pixelsets(PixelSet.objects.none())
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 0

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # Only the 'Omics Unit' column is present
            assert len(pixels_csv) == 1

    def test_export_pixelset_without_pixels(self):

        pixel_sets = factories.PixelSetFactory.create_batch(1)

        zip_archive = self._export_pixelsets(pixel_sets)
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == (2 * len(pixel_sets)) + 1

    def test_export_pixelsets(self):

        pixel_sets = factories.PixelSetFactory.create_batch(1)
        for pixel_set in pixel_sets:
            factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        zip_archive = self._export_pixelsets(pixel_sets)
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

            assert (meta_yaml['pixelsets'][0]['pixelset'] ==
                    pixel_sets[0].get_short_uuid())
            assert (meta_yaml['pixelsets'][0]['description'] ==
                    pixel_sets[0].description)
            # columns are 0-based numbered
            assert meta_yaml['pixelsets'][0]['columns'] == [1, 2]

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

    def test_export_merged_pixelsets_ensures_unique_omics_unit_rows(self):

        pixel_sets = factories.PixelSetFactory.create_batch(1)
        for pixel_set in pixel_sets:
            factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        zip_archive = self._export_pixelsets(
            [*list(pixel_sets), *list(pixel_sets)]
        )
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

    def test_export_merged_pixelsets(self):

        pixel_sets = factories.PixelSetFactory.create_batch(3)
        pixels = factories.PixelFactory.create_batch(3)

        # we add pixels on the same set
        pixel_sets[0].pixels.add(*pixels)

        zip_archive = self._export_pixelsets(list(pixel_sets))
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 3

            assert (meta_yaml['pixelsets'][0]['pixelset'] ==
                    pixel_sets[0].get_short_uuid())
            assert (meta_yaml['pixelsets'][1]['pixelset'] ==
                    pixel_sets[1].get_short_uuid())
            assert (meta_yaml['pixelsets'][2]['pixelset'] ==
                    pixel_sets[2].get_short_uuid())

            assert meta_yaml['pixelsets'][0]['columns'] == [1, 2]
            assert meta_yaml['pixelsets'][1]['columns'] == [3, 4]
            assert meta_yaml['pixelsets'][2]['columns'] == [5, 6]

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

            col_0 = 'Omics Unit'
            col_1 = f'Value {pixel_sets[0].get_short_uuid()}'
            col_2 = f'QS {pixel_sets[0].get_short_uuid()}'
            col_3 = f'Value {pixel_sets[1].get_short_uuid()}'
            col_4 = f'QS {pixel_sets[1].get_short_uuid()}'
            col_5 = f'Value {pixel_sets[2].get_short_uuid()}'
            col_6 = f'QS {pixel_sets[2].get_short_uuid()}'

            assert col_0 in pixels_csv
            assert col_1 in pixels_csv
            assert col_2 in pixels_csv
            assert col_3 in pixels_csv
            assert col_4 in pixels_csv
            assert col_5 in pixels_csv
            assert col_6 in pixels_csv

            # first pixel set is the only one with pixels
            for column_name in (col_1, col_2,):
                assert all(
                    map(
                        lambda value: not pandas.isna(value),
                        pixels_csv[column_name].values()
                    )
                )

            # other pixel sets do not have the omics units
            for column_name in (col_3, col_4, col_5, col_6,):
                assert all(
                    map(
                        lambda value: pandas.isna(value),
                        pixels_csv[column_name].values()
                    )
                )

            for pixel in pixels:
                # pixels are not ordered in the pixel set, so we have to find
                # the corresponding row index for each pixel.
                row = [index for index, value in pixels_csv[col_0].items() if
                       value == pixel.omics_unit.reference.identifier][0]

                assert pixels_csv[col_1][row] == pytest.approx(pixel.value)
                assert (pixels_csv[col_2][row] ==
                        pytest.approx(pixel.quality_score))


class ExportPixelsTestCase(CoreFixturesTestCase):

    def _export_pixels(self, pixel_set):

        csv = export_pixels(pixel_set)
        csv.seek(0)
        return pandas.read_csv(csv).to_dict()

    def test_export_empty_pixelset(self):

        pixel_set = factories.PixelSetFactory.create()

        pixels_csv = self._export_pixels(pixel_set)

        assert len(pixels_csv) == 3

        assert 'Omics Unit' in pixels_csv
        assert 'Value' in pixels_csv
        assert 'QS' in pixels_csv

    def test_export_pixels(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        pixels_csv = self._export_pixels(pixel_set)

        assert len(pixels_csv) == 3

        print(pixels_csv)
        for pixel in pixels:
            # pixels are not ordered in the pixel set, so we have to find
            # the corresponding row index for each pixel.
            row = [index for index, value in pixels_csv['Omics Unit'].items()
                   if value == pixel.omics_unit.reference.identifier][0]

            assert pixels_csv['Value'][row] == str(pixel.value)
            assert pixels_csv['QS'][row] == str(pixel.quality_score)
