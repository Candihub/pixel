import pandas
import pytest
import yaml
import zipfile

from apps.core import factories
from apps.core.models import PixelSet
from apps.core.tests import CoreFixturesTestCase
from apps.data.factories import EntryFactory

from ...utils import (
    PIXELSET_EXPORT_META_FILENAME, PIXELSET_EXPORT_PIXELS_FILENAME,
    export_pixelsets, export_pixels, export_pixelsets_as_html,
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

            # Only the 'Omics Unit' and 'Description columns are present
            assert len(pixels_csv) == 2

    def test_export_pixelset_without_pixels(self):

        pixel_sets = factories.PixelSetFactory.create_batch(1)

        zip_archive = self._export_pixelsets(pixel_sets)
        self._assert_archive_is_valid(zip_archive)

        with zip_archive.open(PIXELSET_EXPORT_META_FILENAME) as meta_file:
            meta_yaml = yaml.load(meta_file)

            assert len(meta_yaml['pixelsets']) == 1

        with zip_archive.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
            pixels_csv = pandas.read_csv(pixels_file).to_dict()

            # 'Omics Unit', 'Description' columns + 2 columns per pixel set
            assert len(pixels_csv) == (2 * len(pixel_sets)) + 2

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

            # 'Omics Unit', 'Description' columns + 2 columns per pixel set
            assert len(pixels_csv) == (2 * len(pixel_sets)) + 2

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

            # 'Omics Unit', 'Description' columns + 2 columns per pixel set
            assert len(pixels_csv) == (2 * len(pixel_sets)) + 2

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

            # 'Omics Unit', 'Description' columns + 2 columns per pixel set
            assert len(pixels_csv) == (2 * len(pixel_sets)) + 2

            col_0 = 'Omics Unit'
            col_1 = 'Description'
            col_2 = f'Value {pixel_sets[0].get_short_uuid()}'
            col_3 = f'QS {pixel_sets[0].get_short_uuid()}'
            col_4 = f'Value {pixel_sets[1].get_short_uuid()}'
            col_5 = f'QS {pixel_sets[1].get_short_uuid()}'
            col_6 = f'Value {pixel_sets[2].get_short_uuid()}'
            col_7 = f'QS {pixel_sets[2].get_short_uuid()}'

            assert col_0 in pixels_csv
            assert col_1 in pixels_csv
            assert col_2 in pixels_csv
            assert col_3 in pixels_csv
            assert col_4 in pixels_csv
            assert col_5 in pixels_csv
            assert col_6 in pixels_csv
            assert col_7 in pixels_csv

            # first pixel set is the only one with pixels
            for column_name in (col_2, col_3,):
                assert all(
                    map(
                        lambda value: not pandas.isna(value),
                        pixels_csv[column_name].values()
                    )
                )

            # other pixel sets do not have the omics units
            for column_name in (col_4, col_5, col_6, col_7,):
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

                assert pixels_csv[col_2][row] == pytest.approx(pixel.value)
                assert (pixels_csv[col_3][row] ==
                        pytest.approx(pixel.quality_score))


class ExportPixelsTestCase(CoreFixturesTestCase):

    def _export_pixels(self, pixel_set, search_terms=None):

        csv = export_pixels(pixel_set, search_terms=search_terms)
        csv.seek(0)
        return pandas.read_csv(csv).to_dict()

    def test_export_empty_pixelset(self):

        pixel_set = factories.PixelSetFactory.create()

        pixels_csv = self._export_pixels(pixel_set)

        assert len(pixels_csv) == 3

        assert 'Omics Unit' in pixels_csv
        assert 'Value' in pixels_csv
        assert 'QS' in pixels_csv

    def test_export_all_pixels_when_no_search_terms_supplied(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(3, pixel_set=pixel_set)

        pixels_csv = self._export_pixels(pixel_set)

        assert len(pixels_csv) == 3
        assert len(pixels_csv['Omics Unit'].items()) == 3

        for pixel in pixels:
            # pixels are not ordered in the pixel set, so we have to find
            # the corresponding row index for each pixel.
            row = [index for index, value in pixels_csv['Omics Unit'].items()
                   if value == pixel.omics_unit.reference.identifier][0]

            assert pixels_csv['Value'][row] == pytest.approx(pixel.value)
            assert pixels_csv['QS'][row] == pytest.approx(pixel.quality_score)

    def test_export_pixels_with_specific_omics_units(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(3, pixel_set=pixel_set)
        selected_pixel = pixels[1]

        pixels_csv = self._export_pixels(
            pixel_set,
            search_terms=[selected_pixel.omics_unit.reference.identifier]
        )

        assert len(pixels_csv['Omics Unit'].items()) == 1

        assert (pixels_csv['Omics Unit'][0] ==
                selected_pixel.omics_unit.reference.identifier)
        assert pixels_csv['Value'][0] == pytest.approx(selected_pixel.value)
        assert (pixels_csv['QS'][0] ==
                pytest.approx(selected_pixel.quality_score))


class ExportPixelsetsAsHtmlTestCase(CoreFixturesTestCase):

    def assertNotInHTML(self, needle, haystack):

        return self.assertInHTML(needle, haystack, count=0)

    def test_returns_empty_table(self):

        expected = """
        <table class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>Omics Unit</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr class="empty">
              <td colspan="3">
                Your selection gave no results
              </td>
            </tr>
          </tbody>
        </table>
        """

        html = export_pixelsets_as_html(pixel_set_ids=[])
        self.assertHTMLEqual(html, expected)

    def test_creates_columns(self):

        pixel_sets = factories.PixelSetFactory.create_batch(2)

        expected = """
        <table class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>Omics Unit</th>
              <th>Description</th>
              <th>Value {id_1}</th>
              <th>QS {id_1}</th>
              <th>Value {id_2}</th>
              <th>QS {id_2}</th>
            </tr>
          </thead>
          <tbody>
            <tr class="empty">
              <td colspan="7">
                Your selection gave no results
              </td>
            </tr>
          </tbody>
        </table>
        """.format(
          id_1=pixel_sets[0].get_short_uuid(),
          id_2=pixel_sets[1].get_short_uuid(),
        )

        pixel_set_ids = [pixelset.id for pixelset in pixel_sets]

        html = export_pixelsets_as_html(pixel_set_ids=pixel_set_ids)
        self.assertHTMLEqual(html, expected)

    def test_allows_string_ids(self):

        pixel_sets = factories.PixelSetFactory.create_batch(2)

        expected = """
        <table class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>Omics Unit</th>
              <th>Description</th>
              <th>Value {id_1}</th>
              <th>QS {id_1}</th>
              <th>Value {id_2}</th>
              <th>QS {id_2}</th>
            </tr>
          </thead>
          <tbody>
            <tr class="empty">
              <td colspan="7">
                Your selection gave no results
              </td>
            </tr>
          </tbody>
        </table>
        """.format(
          id_1=pixel_sets[0].get_short_uuid(),
          id_2=pixel_sets[1].get_short_uuid(),
        )

        # here, we create str ids to make sure the function handles uuid.UUID
        # and string ids.
        pixel_set_ids = [str(pixelset.id) for pixelset in pixel_sets]

        html = export_pixelsets_as_html(pixel_set_ids=pixel_set_ids)
        self.assertHTMLEqual(html, expected)

    def test_renders_pixels(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(
          2,
          pixel_set=pixel_set
        )

        pixel_set_ids = [pixel_set.id]
        reference_1 = pixels[0].omics_unit.reference
        reference_2 = pixels[1].omics_unit.reference

        expected_row_1 = """
        <tr>
          <th>0</th>
          <td><a href="{url}">{identifier}</a></td>
          <td>{description}</td>
          <td>{value}</td>
          <td>{quality_score}</td>
        </tr>
        """.format(
          url=reference_1.url,
          identifier=reference_1.identifier,
          description=reference_1.description,
          value=pixels[0].value,
          quality_score=pixels[0].quality_score,
        )

        expected_row_2 = """
        <tr>
          <th>1</th>
          <td><a href="{url}">{identifier}</a></td>
          <td>{description}</td>
          <td>{value}</td>
          <td>{quality_score}</td>
        </tr>
        """.format(
          url=reference_2.url,
          identifier=reference_2.identifier,
          description=reference_2.description,
          value=pixels[1].value,
          quality_score=pixels[1].quality_score,
        )

        html = export_pixelsets_as_html(pixel_set_ids=pixel_set_ids)
        self.assertInHTML(expected_row_1, html)
        self.assertInHTML(expected_row_2, html)

    def test_limits_number_of_rows(self):

        pixel_set = factories.PixelSetFactory.create()
        factories.PixelFactory.create_batch(2, pixel_set=pixel_set)

        pixel_set_ids = [pixel_set.id]

        html = export_pixelsets_as_html(
          pixel_set_ids=pixel_set_ids,
          display_limit=1
        )
        self.assertInHTML('<th>0</th>', html)
        self.assertNotInHTML('<th>1</th>', html)

    def test_filters_by_omics_units(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(
          2,
          pixel_set=pixel_set
        )

        pixel_set_ids = [pixel_set.id]
        omics_units = [pixels[0].omics_unit.reference.identifier]

        html = export_pixelsets_as_html(
          pixel_set_ids=pixel_set_ids,
          search_terms=omics_units,
        )
        self.assertInHTML('<th>0</th>', html)
        self.assertNotInHTML('<th>1</th>', html)

    def test_fills_rows_correctly(self):

        entity = EntryFactory.create()
        pixel_sets = factories.PixelSetFactory.create_batch(2)
        pixel_1 = factories.PixelFactory.create(
          omics_unit__reference=entity,
          pixel_set=pixel_sets[0]
        )
        pixel_2 = factories.PixelFactory.create(
            omics_unit__reference=entity,
            pixel_set=pixel_sets[1]
        )

        pixel_set_ids = [pixel_set.id for pixel_set in pixel_sets]

        expected_row = """
        <tr>
          <th>0</th>
          <td><a href="{url}">{identifier}</a></td>
          <td>{description}</td>
          <td>{value_1}</td>
          <td>{quality_score_1}</td>
          <td>{value_2}</td>
          <td>{quality_score_2}</td>
        </tr>
        """.format(
          url=entity.url,
          identifier=entity.identifier,
          description=entity.description,
          value_1=pixel_1.value,
          quality_score_1=pixel_1.quality_score,
          value_2=pixel_2.value,
          quality_score_2=pixel_2.quality_score,
        )

        html = export_pixelsets_as_html(pixel_set_ids=pixel_set_ids)
        self.assertInHTML(expected_row, html)
