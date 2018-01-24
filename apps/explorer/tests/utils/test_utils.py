import pandas
import yaml

from ...utils import export_pixelsets
from apps.core.models import PixelSet
from apps.core.tests import CoreFixturesTestCase
from apps.core import factories


class ExportPixelsSetTestCase(CoreFixturesTestCase):

    def _assert_archive_is_valid(self, zip_archive):
        assert len(zip_archive.namelist()) == 2
        assert 'meta.yaml' in zip_archive.namelist()
        assert 'pixels.csv' in zip_archive.namelist()

    def test_export_no_pixels(self):
        zip_archive = export_pixelsets(PixelSet.objects.none())
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open('meta.yaml') as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 0

        with zip_archive.open('pixels.csv') as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # Only the 'Omics Unit' column is present
            assert len(pixels_csv) == 1

    def test_export_pixels_without_analyses(self):
        pixel_sets = factories.PixelSetFactory.create_batch(1)

        zip_archive = export_pixelsets(pixel_sets)
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open('meta.yaml') as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

        with zip_archive.open('pixels.csv') as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

    def test_export_pixels(self):
        pixel_sets = factories.PixelSetFactory.create_batch(1)
        for pixel_set in pixel_sets:
            factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        zip_archive = export_pixelsets(pixel_sets)
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open('meta.yaml') as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

            assert (meta_yaml['pixelsets'][0]['pixelset'] ==
                    pixel_sets[0].get_short_uuid())
            assert (meta_yaml['pixelsets'][0]['description'] ==
                    pixel_sets[0].description)
            # columns are 0-based numbered
            assert meta_yaml['pixelsets'][0]['columns'] == [1, 2]

        with zip_archive.open('pixels.csv') as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

    def test_export_pixels_merge_ensures_unique_omics_unit_rows(self):
        pixel_sets = factories.PixelSetFactory.create_batch(1)
        for pixel_set in pixel_sets:
            factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        zip_archive = export_pixelsets([*list(pixel_sets), *list(pixel_sets)])
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open('meta.yaml') as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

        with zip_archive.open('pixels.csv') as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit' column + 2 columns per pixel set
            assert len(pixels_csv) == 2 * len(pixel_sets) + 1

    def test_export_pixels_merge_multiple_sets(self):
        pixel_sets = factories.PixelSetFactory.create_batch(3)
        pixels = factories.PixelFactory.create_batch(3)

        # we add pixels on the same set
        pixel_sets[0].pixels.add(pixels[0])
        pixel_sets[0].pixels.add(pixels[1])
        pixel_sets[0].pixels.add(pixels[2])

        zip_archive = export_pixelsets(list(pixel_sets))
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open('meta.yaml') as meta_file:
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

        with zip_archive.open('pixels.csv') as pixels_file:
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
