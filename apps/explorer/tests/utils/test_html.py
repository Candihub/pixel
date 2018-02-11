from apps.core import factories
from apps.core.tests import CoreFixturesTestCase
from apps.explorer.utils import create_html_table_for_pixelsets


class CreateHtmlTableForPixelSetsTestCase(CoreFixturesTestCase):

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
          </tbody>
        </table>
        """

        html = create_html_table_for_pixelsets(pixel_set_ids=[])
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
          </tbody>
        </table>
        """.format(
          id_1=pixel_sets[0].get_short_uuid(),
          id_2=pixel_sets[1].get_short_uuid(),
        )

        pixel_set_ids = [pixelset.id for pixelset in pixel_sets]

        html = create_html_table_for_pixelsets(pixel_set_ids=pixel_set_ids)
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
          </tbody>
        </table>
        """.format(
          id_1=pixel_sets[0].get_short_uuid(),
          id_2=pixel_sets[1].get_short_uuid(),
        )

        # here, we create str ids to make sure the function handles uuid.UUID
        # and string ids.
        pixel_set_ids = [str(pixelset.id) for pixelset in pixel_sets]

        html = create_html_table_for_pixelsets(pixel_set_ids=pixel_set_ids)
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

        html = create_html_table_for_pixelsets(pixel_set_ids=pixel_set_ids)
        self.assertInHTML(expected_row_1, html)
        self.assertInHTML(expected_row_2, html)

    def test_limits_number_of_rows(self):

        pixel_set = factories.PixelSetFactory.create()
        factories.PixelFactory.create_batch(2, pixel_set=pixel_set)

        pixel_set_ids = [pixel_set.id]

        html = create_html_table_for_pixelsets(
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

        html = create_html_table_for_pixelsets(
          pixel_set_ids=pixel_set_ids,
          omics_units=omics_units,
        )
        self.assertInHTML('<th>0</th>', html)
        self.assertNotInHTML('<th>1</th>', html)
