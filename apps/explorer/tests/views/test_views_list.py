import datetime
import pandas

from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as date_filter
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
from apps.explorer.utils import PIXELSET_EXPORT_PIXELS_FILENAME
from apps.explorer.views import PixelSetExportView
from apps.explorer.views.helpers import get_selected_pixel_sets_from_session
from apps.explorer.views.views_detail import GetSearchTermsMixin


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
            'No Pixel Set matches your query'
            '</td>'
        )
        self.assertContains(response, expected, html=True)

    def test_does_not_render_export_button_when_no_pixelsets(self):

        response = self.client.get(self.url)

        expected = (
            '<button type="submit" class="button">',
            '<i class="fa fa-download" aria-hidden="true"></i>'
            'Download an archive (.zip) with the selected Pixel Sets',
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

    def test_renders_completion_dates(self):

        make_development_fixtures(n_pixel_sets=1)
        response = self.client.get(self.url)

        expected = (
            '<span class="completed-at">'
            'Completion date: {}'
            '</span>'
        )

        pixelset = models.PixelSet.objects.get()

        self.assertContains(
            response,
            expected.format(
                date_filter(pixelset.analysis.completed_at)
            ),
            count=1,
            html=True
        )
        self.assertContains(
            response,
            expected.format(
                date_filter(pixelset.analysis.experiments.get().completed_at)
            ),
            count=1,
            html=True
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

        # We generate one pixel per pixelset so that half of Pixel Sets
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

    def test_omics_areas_tree_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create a parent omics area and link it to a Pixel Set
        parent_omics_area = factories.OmicsAreaFactory()
        first_experiment = factories.ExperimentFactory(
            omics_area=parent_omics_area
        )
        first_analysis = factories.AnalysisFactory(
            experiments=[first_experiment, ]
        )
        first_pixelset = factories.PixelSetFactory(
            analysis=first_analysis
        )

        # Create a child omics are and link it to a Pixel Set
        child_omics_area = factories.OmicsAreaFactory(
            parent=parent_omics_area
        )
        second_experiment = factories.ExperimentFactory(
            omics_area=child_omics_area
        )
        second_analysis = factories.AnalysisFactory(
            experiments=[second_experiment, ]
        )
        second_pixelset = factories.PixelSetFactory(
            analysis=second_analysis
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=10
        )

        # omics_areas filter
        data = {
            'omics_areas': [child_omics_area.id, ]
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
                '<a'
                f'  href="{second_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(second_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )

        data = {
            'omics_areas': [parent_omics_area.id, ]
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
                '<a'
                f'  href="{first_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(first_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )

        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<a'
                f'  href="{second_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(second_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
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

    def test_tags_tree_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create two pixelsets with tags
        omics_area = factories.OmicsAreaFactory()
        experiment = factories.ExperimentFactory(
            omics_area=omics_area
        )
        first_analysis = factories.AnalysisFactory(
            experiments=[experiment, ]
        )
        first_analysis_tags = 'candida/glabrata/cbs138'
        first_analysis.tags = first_analysis_tags
        first_analysis.save()
        first_pixelset = factories.PixelSetFactory(
            analysis=first_analysis
        )
        second_analysis = factories.AnalysisFactory(
            experiments=[experiment, ]
        )
        second_analysis_tags = 'candida'
        second_analysis.tags = second_analysis_tags
        second_analysis.save()
        second_pixelset = factories.PixelSetFactory(
            analysis=second_analysis
        )

        # no filter
        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=10
        )

        # tags filter
        tag = models.Tag.objects.get(name=first_analysis_tags)
        data = {
            'tags': [tag.id, ]
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
                '<a'
                f'  href="{first_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(first_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )

        tag = models.Tag.objects.get(name=second_analysis_tags)
        data = {
            'tags': [tag.id, ]
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
                '<a'
                f'  href="{first_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(first_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )
        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<a'
                f'  href="{second_pixelset.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(second_pixelset.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )

    def test_all_filters(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create a special Pixel Set which will match all filters
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
                'No Pixel Set matches your query'
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
                '<a'
                f'  href="{pixel_set.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(pixel_set.pixels_file.name)}'
                '</a>'
                '</td>'
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

        first_pixel_set = models.PixelSet.objects.all().first()
        second_pixel_set = models.PixelSet.objects.all().last()

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

        first_pixel_set.analysis = first_analysis
        first_pixel_set.save()

        experiment = factories.ExperimentFactory(
            description=(
                'Qapla. Dah tlhingan hol mu ghom a dalegh. Qawhaqvam '
                'chenmohlu di wiqipe diya ohvad ponglu. Ach jinmolvamvad '
                'Saghbe law tlhingan hol, dis, oh mevmohlu.'
            )
        )
        second_analysis = factories.AnalysisFactory(experiments=[experiment, ])

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
                '<a'
                f'  href="{first_pixel_set.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(first_pixel_set.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )
        self.assertContains(
            response,
            (
                '<td class="filename">'
                '<a'
                f'  href="{second_pixel_set.get_absolute_url()}"'
                '  title="More information about this Pixel Set"'
                '>'
                '<!-- Pixel Set file name -->'
                f'{filename(second_pixel_set.pixels_file.name)}'
                '</a>'
                '</td>'
            ),
            count=1,
            html=True,
        )

    def test_search_is_case_insensitive(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        first_pixel_set = models.PixelSet.objects.all().first()
        second_pixel_set = models.PixelSet.objects.all().last()

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

        first_pixel_set.analysis = first_analysis
        first_pixel_set.save()

        experiment = factories.ExperimentFactory(
            description=(
                'Qapla. Dah tlhingan hol mu ghom a dalegh. Qawhaqvam '
                'chenmohlu di wiqipe diya ohvad ponglu. Ach jinmolvamvad '
                'Saghbe law tlhingan hol, dis, oh mevmohlu.'
            )
        )
        second_analysis = factories.AnalysisFactory(experiments=[experiment, ])

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
            'search': 'JINMOLVAMVAD'
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=2
        )


class PixelSetSelectViewTestCase(CoreFixturesTestCase):

    def setUp(self):

        super().setUp()

        self.user = factories.PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=self.user.username,
            password=factories.PIXELER_PASSWORD,
        )
        self.url = reverse('explorer:pixelset_select')

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

    def test_stores_selection_in_user_session(self):

        pixel_sets = factories.PixelSetFactory.create_batch(2)
        pixel_sets_ids = [str(p.id) for p in pixel_sets]

        self.assertIsNone(self.client.session.get('explorer'))

        response = self.client.post(self.url, {
            'pixel_sets': pixel_sets_ids
        })

        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(self.client.session.get('explorer'))

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )

        self.assertIsNotNone(session_pixel_sets)
        self.assertEqual(len(pixel_sets_ids), len(session_pixel_sets))

        for pixel_sets_id in pixel_sets_ids:
            self.assertIn(pixel_sets_id, session_pixel_sets)

    def test_adds_new_selection_in_user_session(self):

        # First Pixel Sets selection
        pixel_sets = factories.PixelSetFactory.create_batch(2)
        pixel_sets_ids = [str(p.id) for p in pixel_sets]

        data = {'pixel_sets': pixel_sets_ids}
        self.client.post(self.url, data, follow=True)

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(pixel_sets_ids), len(session_pixel_sets))

        # Second Pixel Set seletion
        new_pixel_sets = factories.PixelSetFactory.create_batch(2)
        new_pixel_sets_ids = [str(p.id) for p in new_pixel_sets]

        data = {'pixel_sets': new_pixel_sets_ids}
        self.client.post(self.url, data, follow=True)

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(
            len(pixel_sets_ids + new_pixel_sets_ids),
            len(session_pixel_sets)
        )

    def test_renders_message_on_success(self):

        pixel_sets = factories.PixelSetFactory.create_batch(2)
        pixel_sets_ids = [str(p.id) for p in pixel_sets]

        response = self.client.post(
            self.url,
            {
                'pixel_sets': pixel_sets_ids
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            (
                '<div class="message success">'
                '2 Pixel Sets have been added to your selection.'
                '</div>'
            ),
            html=True
        )


class PixelSetClearViewTestCase(CoreFixturesTestCase):

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
        self.url = reverse('explorer:pixelset_clear')
        self.pixel_sets = []

    def _select_pixel_sets(self):

        self.pixel_sets = factories.PixelSetFactory.create_batch(2)
        data = {
            'pixel_sets': [str(p.id) for p in self.pixel_sets]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

    def test_redirects_to_list_view_when_done(self):

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('explorer:pixelset_list'))

    def test_clears_selection(self):

        self._select_pixel_sets()

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(session_pixel_sets), len(self.pixel_sets))

        self.client.post(self.url, {}, follow=True)

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(session_pixel_sets), 0)

    def test_renders_message_on_success(self):

        self._select_pixel_sets()

        response = self.client.post(self.url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            (
                '<div class="message success">'
                'Pixel Set selection has been cleared.'
                '</div>'
            ),
            html=True
        )


class PixelSetDeselectViewTestCase(CoreFixturesTestCase):

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
        self.url = reverse('explorer:pixelset_deselect')
        self.pixel_sets = factories.PixelSetFactory.create_batch(2)
        data = {
            'pixel_sets': [str(p.id) for p in self.pixel_sets]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

    def test_redirects_to_list_view_when_done(self):

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('explorer:pixelset_list'))

    def test_deselect(self):

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(session_pixel_sets), len(self.pixel_sets))

        data = {
            'pixel_set': str(self.pixel_sets[0].id)
        }
        self.client.post(self.url, data, follow=True)
        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(session_pixel_sets), 1)

        data = {
            'pixel_set': str(self.pixel_sets[1].id)
        }
        self.client.post(self.url, data, follow=True)
        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.client.session
        )
        self.assertEqual(len(session_pixel_sets), 0)

    def test_renders_message_on_success(self):

        pixel_set = self.pixel_sets[0]

        data = {
            'pixel_set': str(pixel_set.id)
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            (
                '<div class="message success">'
                "Pixel Set {} has been removed from selection."
                '</div>'
            ).format(
                str(pixel_set.id)
            ),
            html=True
        )

    def test_renders_message_on_failure(self):

        fake_id = 'fake'
        data = {
            'pixel_set': fake_id
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            (
                f'Select a valid choice. {fake_id} is not one of the '
                'available choices.'
            ),
            html=True
        )


class PixelSetExportViewTestCase(GetSearchTermsMixin, CoreFixturesTestCase):

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

    def test_returns_zip_file(self):

        fake_dt = timezone.make_aware(datetime.datetime(2018, 1, 12, 11, 00))

        with patch.object(timezone, 'now', return_value=fake_dt):

            # Save Pixel Sets in user session
            pixel_sets = factories.PixelSetFactory.create_batch(2)
            data = {
                'pixel_sets': [str(p.id) for p in pixel_sets]
            }
            self.client.post(
                reverse('explorer:pixelset_select'), data, follow=True
            )

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/zip')
            self.assertEqual(
                response['Content-Disposition'],
                'attachment; filename={}'.format(
                    PixelSetExportView.get_export_archive_filename()
                )
            )

            try:
                zip = ZipFile(BytesIO(response.content), 'r')
                self.assertIsNone(zip.testzip())
            finally:
                zip.close()

    def test_displays_message_after_redirect_when_selection_is_empty(self):

        response = self.client.get(self.url, follow=True)

        self.assertContains(
            response,
            (
                '<div class="message error">'
                'Cannot export an empty selection.'
                '</div>'
            ),
            html=True
        )

    def test_filters_omics_units(self):

        pixel_set = factories.PixelSetFactory.create()
        pixels = factories.PixelFactory.create_batch(2, pixel_set=pixel_set)

        # select pixel set, otherwise we cannot set omics units
        self.client.post(
            reverse('explorer:pixelset_select'),
            {'pixel_sets': [pixel_set.id]},
            follow=True
        )
        response = self.client.get(self.url)

        self.assertIsNone(
            self.get_search_terms(self.client.session, default=None)
        )

        selected_pixel = pixels[1]

        # set search terms in session
        response = self.client.post(reverse('explorer:pixelset_selection'), {
            'search_terms': selected_pixel.omics_unit.reference.identifier,
        }, follow=True)

        fake_dt = timezone.make_aware(datetime.datetime(2018, 1, 12, 11, 00))

        with patch.object(timezone, 'now', return_value=fake_dt):

            response = self.client.get('{}?{}=1'.format(
                self.url,
                PixelSetExportView.SUBSET_QUERY_PARAM,
            ))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/zip')
            self.assertEqual(
                response['Content-Disposition'],
                'attachment; filename={}'.format(
                    PixelSetExportView.get_export_archive_filename()
                )
            )

            try:
                zip = ZipFile(BytesIO(response.content), 'r')
                self.assertIsNone(zip.testzip())

                with zip.open(PIXELSET_EXPORT_PIXELS_FILENAME) as pixels_file:
                    pixels_csv = pandas.read_csv(pixels_file)
                    self.assertEqual(len(pixels_csv.index), 1)
            finally:
                zip.close()
