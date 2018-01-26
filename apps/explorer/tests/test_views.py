import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone
from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

from apps.core import factories, models
from apps.core.templatetags.files import filename
from apps.core.tests import CoreFixturesTestCase
from apps.core.management.commands.make_development_fixtures import (
    make_development_fixtures
)
from apps.explorer.views import PixelSetExportView


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

    def test_does_not_render_export_button_when_no_pixelsets(self):

        response = self.client.get(self.url)

        expected = (
            '<button type="submit" class="button">',
            '<i class="fa fa-download" aria-hidden="true"></i>'
            'Download an archive (.zip) with the selected Pixel sets',
            '</button>'
        )

        self.assertNotContains(response, expected, html=True)

    def test_renders_pixelset_list(self):

        make_development_fixtures(n_pixel_sets=12)
        response = self.client.get(self.url)

        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=10
        )
        self.assertContains(
            response,
            '<button type="submit" class="button">',
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
            count=(n_pixel_sets // 2)
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

    def test_search_filter_with_omics_unit_reference(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        pixel_set = models.PixelSet.objects.all()[4]
        reference = pixel_set.pixels.get().omics_unit.reference.identifier

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=8
        )

        # filter with Omics Unit reference identifier search
        data = {
            'search': reference
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=1
        )
        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<!-- Pixel set file name -->'
                '{}'
                '</td>'
            ).format(
                filename(pixel_set.pixels_file.name)
            ),
            count=1,
            html=True,
        )

    def test_search_filter_with_keywords(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Add custom descriptions written in Klingon so that we are pretty
        # sure nothing will match our query 🤓
        #
        # Lorem ipsum source:
        # http://shooshee.tumblr.com/post/212964026/klingon-lorem-ipsum
        first_analysis = factories.AnalysisFactory(
            description=(
                'Qapla. Dah tlhingan hol mu ghom a dalegh. Qawhaqvam '
                'chenmohlu di wiqipe diya ohvad ponglu. Ach jinmolvamvad '
                'Saghbe law tlhingan hol, dis, oh mevmohlu.'
            )
        )

        experiment = factories.ExperimentFactory(
            description=(
                'Qapla. Dah tlhingan hol mu ghom a dalegh. Qawhaqvam '
                'chenmohlu di wiqipe diya ohvad ponglu. Ach jinmolvamvad '
                'Saghbe law tlhingan hol, dis, oh mevmohlu.'
            )
        )
        second_analysis = factories.AnalysisFactory(experiments=[experiment, ])

        first_pixel_set = models.PixelSet.objects.all()[4]
        first_pixel_set.analysis = first_analysis
        first_pixel_set.save()

        second_pixel_set = models.PixelSet.objects.all()[6]
        second_pixel_set.analysis = second_analysis
        second_pixel_set.save()

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=8
        )

        # filter with keyword search
        data = {
            'search': 'jinmolvamvad'
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=2
        )
        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<!-- Pixel set file name -->'
                f'{filename(first_pixel_set.pixels_file.name)}'
                '</td>'
            ),
            count=1,
            html=True,
        )
        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<!-- Pixel set file name -->'
                f'{filename(second_pixel_set.pixels_file.name)}'
                '</td>'
            ),
            count=1,
            html=True,
        )


class PixelSetExportViewTestCase(CoreFixturesTestCase):

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
        self.url = reverse('explorer:pixelset_export')

    def test_redirects_to_list_view_when_invalid(self):

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('explorer:pixelset_list'))

    def test_redirects_to_previous_url_if_provided_when_invalid(self):

        redirect_to = '/?q=123'
        response = self.client.post(self.url, {'redirect_to': redirect_to})

        self.assertRedirects(response, redirect_to)

    def test_displays_message_after_redirect_when_invalid(self):

        response = self.client.post(self.url, follow=True)

        self.assertContains(
            response,
            (
                '<div class="message error">'
                'You must select at least one Pixel Set.'
                '</div>'
            ),
            html=True
        )

    def test_returns_zip_file(self):

        fake_dt = timezone.make_aware(datetime.datetime(2018, 1, 12, 11, 00))

        with patch.object(timezone, 'now', return_value=fake_dt):
            pixel_sets = factories.PixelSetFactory.create_batch(1)

            response = self.client.post(self.url, {
                'pixel_sets': [pixel_sets[0].id]
            })

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/zip')
            self.assertEqual(
                response['Content-Disposition'],
                'attachment; filename={}'.format(
                    PixelSetExportView.ATTACHEMENT_FILENAME.format(
                        date_time=fake_dt.strftime('%Y%m%d_%Hh%Mm%Ss')
                    )
                )
            )

            try:
                zip = ZipFile(BytesIO(response.content), 'r')
                self.assertIsNone(zip.testzip())
            finally:
                zip.close()
