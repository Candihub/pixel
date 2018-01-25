from django.core.urlresolvers import reverse

from apps.core import factories, models
from apps.core.tests import CoreFixturesTestCase
from apps.core.management.commands.make_development_fixtures import (
    make_development_fixtures
)


class PixelSetListViewTestCase(CoreFixturesTestCase):

    def setUp(self):

        self.user = factories.PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=self.user.username,
            password=factories.PIXELER_PASSWORD,
        )
        self.url = reverse('explorer:pixelset_list')

    def test_renders_pixelset_list_template(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explorer/pixelset_list.html')

    def test_renders_empty_message(self):

        response = self.client.get(self.url)

        expected = (
            '<td colspan="8" class="empty">'
            'No pixel set matches your query'
            '</td>'
        )
        self.assertContains(response, expected, html=True)

    def test_renders_pixelset_list(self):

        make_development_fixtures(n_pixel_sets=12)
        response = self.client.get(self.url)

        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=10
        )

    def test_species_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create our special ones
        species = factories.SpeciesFactory()
        strain = factories.StrainFactory(species=species)
        n_new_pixel_sets = 2
        pixel_sets = factories.PixelSetFactory.create_batch(n_new_pixel_sets)

        omics_units = factories.OmicsUnitFactory.create_batch(
            n_new_pixel_sets,
            strain=strain
        )
        for omics_unit, pixel_set in zip(omics_units, pixel_sets):
            factories.PixelFactory(
                omics_unit=omics_unit,
                pixel_set=pixel_set,
            )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=10
        )

        # species filter
        data = {
            'species': [species.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=n_new_pixel_sets
        )

    def test_omics_unit_types_filter(self):

        # We generate one pixel per pixelset so that half of pixel sets
        # contains pixels with 'mRNA' omics unit type and the other half
        # 'protein' omics unit type
        n_pixel_sets = 8
        make_development_fixtures(
            n_pixel_sets=n_pixel_sets,
            n_pixels_per_set=1
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=n_pixel_sets
        )

        # omics_unit_types filter
        omics_unit_type = models.OmicsUnitType.objects.first()
        data = {
            'omics_unit_types': [omics_unit_type.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=int(n_pixel_sets / 2)
        )

    def test_omics_areas_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        omics_area = factories.OmicsAreaFactory()
        experiment = factories.ExperimentFactory(
            omics_area=omics_area
        )
        analysis = factories.AnalysisFactory(
            experiments=[experiment, ]
        )
        factories.PixelSetFactory(
            analysis=analysis
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=9
        )

        # omics_areas filter
        data = {
            'omics_areas': [omics_area.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=1
        )

    def test_tags_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        omics_area = factories.OmicsAreaFactory()

        experiment = factories.ExperimentFactory(
            omics_area=omics_area
        )
        experiment_tag = 'candida'
        experiment.tags = experiment_tag
        experiment.save()

        analysis = factories.AnalysisFactory(
            experiments=[experiment, ]
        )
        analysis_tag = 'msms/time'
        analysis.tags = analysis_tag
        analysis.save()
        factories.PixelSetFactory(
            analysis=analysis
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=9
        )

        # tags filter
        tag = models.Tag.objects.get(name=experiment_tag)
        data = {
            'tags': [tag.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=1
        )

        tag = models.Tag.objects.get(name=analysis_tag)
        data = {
            'tags': [tag.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=1
        )

    def test_all_filters(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create a special pixel set which will match all filters
        species = factories.SpeciesFactory()
        strain = factories.StrainFactory(species=species)
        omics_unit_type = factories.OmicsUnitTypeFactory()
        omics_unit = factories.OmicsUnitFactory(
            strain=strain,
            type=omics_unit_type,
        )
        omics_area = factories.OmicsAreaFactory()
        experiment = factories.ExperimentFactory(
            omics_area=omics_area
        )
        experiment_tag = 'candida'
        experiment.tags = experiment_tag
        experiment.save()
        analysis = factories.AnalysisFactory(
            experiments=[experiment, ]
        )
        pixel_set = factories.PixelSetFactory(
            analysis=analysis
        )
        factories.PixelFactory(
            omics_unit=omics_unit,
            pixel_set=pixel_set,
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=9
        )

        # all filters
        tag = models.Tag.objects.get(name=experiment_tag)
        data = {
            'species': [species.id, ],
            'omics_unit_types': [omics_unit_type.id, ],
            'omics_area': [omics_area.id, ],
            'tags': [tag.id, ],
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=1
        )

    def test_unexpected_filter_value(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=8
        )
        self.assertNotContains(
            response,
            '<small class="error">\'fakeid\' is not a valid UUID.</small>',
            html=True,
        )

        # odd filter query
        data = {
            'species': ['fakeid', ],
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=8
        )
        print(response.content)
        self.assertContains(
            response,
            (
                '<small class="error">'
                '&#39;fakeid&#39; is not a valid UUID.'
                '</small>'
            ),
            html=True,
        )

    def test_filters_with_no_match(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create a new species
        species = factories.SpeciesFactory()

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=8
        )

        # filter with no possible result
        data = {
            'species': [species.id, ]
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=0
        )
        self.assertContains(
            response,
            (
                '<td colspan="8" class="empty">'
                'No pixel set matches your query'
                '</td>'
            ),
            count=1,
            html=True,
        )
