import datetime

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
from apps.explorer.views import (
    PixelSetDetailView, PixelSetExportView, PixelSetExportPixelsView,
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

    def test_omics_areas_tree_filter(self):

        # Create 8 pixelset
        make_development_fixtures(
            n_pixel_sets=8,
            n_pixels_per_set=1
        )

        # Create a parent omics area and link it to a pixel set
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

        # Create a child omics are and link it to a pixel set
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '<a'
                f'  href="{pixel_set.get_absolute_url()}"'
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '<a'
                f'  href="{first_pixel_set.get_absolute_url()}"'
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
                '  title="Click for details about this pixel set"'
                '>'
                '<!-- Pixel set file name -->'
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
            'search': 'JINMOLVAMVAD'
        }
        response = self.client.get(self.url, data)
        self.assertContains(
            response,
            '<tr class="pixelset">',
            count=2
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
                    PixelSetExportView.get_export_archive_filename()
                )
            )

            try:
                zip = ZipFile(BytesIO(response.content), 'r')
                self.assertIsNone(zip.testzip())
            finally:
                zip.close()


class PixelSetDetailViewTestCase(CoreFixturesTestCase):

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

        self.pixel_set = factories.PixelSetFactory()
        self.pixel_set.analysis.experiments.add(
            factories.ExperimentFactory()
        )
        self.n_pixels = 20
        self.pixels = factories.PixelFactory.create_batch(
            self.n_pixels,
            pixel_set=self.pixel_set
        )

        self.url = self.pixel_set.get_absolute_url()

    def test_renders_pixelset_detail_template(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explorer/pixelset_detail.html')

    def test_shows_edition_link_for_staff_users(self):

        response = self.client.get(self.url)

        admin_url = reverse(
            'admin:core_pixelset_change',
            args=(str(self.pixel_set.id), )
        )
        title = 'Edit this pixel set from the admin'
        expected = (
            f'<a href="{admin_url}" title="{title}" class="edit">'
            '<i class="fa fa-pencil" aria-hidden="true"></i>'
            'edit'
            '</a>'
        )
        self.assertContains(
            response,
            expected,
            html=True,
            count=1
        )

    def test_hides_edition_link_for_standard_users(self):

        self.client.logout()

        user = factories.PixelerFactory(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        self.client.login(
            username=user.username,
            password=factories.PIXELER_PASSWORD,
        )

        response = self.client.get(self.url)

        admin_url = reverse(
            'admin:core_pixelset_change',
            args=(str(self.pixel_set.id), )
        )
        title = 'Edit this pixel set from the admin'
        expected = (
            f'<a href="{admin_url}" title="{title}" class="edit">'
            '<i class="fa fa-pencil" aria-hidden="true"></i>'
            'edit'
            '</a>'
        )
        self.assertNotContains(
            response,
            expected,
            html=True,
        )

    def test_show_description_in_pixels_preview(self):

        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<td class="description">',
            count=self.n_pixels
        )

    def test_renders_completion_dates(self):

        response = self.client.get(self.url)

        expected = (
            '<span class="completed-at">'
            'Completion date: {}'
            '</span>'
        )

        self.assertContains(
            response,
            expected.format(
                date_filter(self.pixel_set.analysis.completed_at)
            ),
            count=1,
            html=True
        )
        self.assertContains(
            response,
            expected.format(
                date_filter(
                    self.pixel_set.analysis.experiments.get().completed_at
                )
            ),
            count=1,
            html=True
        )

    def test_renders_release_date(self):

        response = self.client.get(self.url)

        expected = (
            '<span class="released-at">'
            'Release date: {}'
            '</span>'
        )

        self.assertContains(
            response,
            expected.format(
                date_filter(
                    self.pixel_set.analysis.experiments.get().released_at
                )
            ),
            count=1,
            html=True
        )

    def test_pixels_limit(self):

        response = self.client.get(self.url)
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=self.n_pixels
        )

        # Generate a new pixelset with limit+ pixels
        n_pixels = 101
        pixel_set = factories.PixelSetFactory()
        factories.PixelFactory.create_batch(
            n_pixels,
            pixel_set=pixel_set
        )
        response = self.client.get(pixel_set.get_absolute_url())
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=PixelSetDetailView.pixels_limit
        )
        self.assertNotContains(
            response,
            'Download a CSV file with the selected Pixels'
        )

    def test_select_one_pixel(self):

        session = self.client.session
        omics_unit_id = self.pixels[0].omics_unit.reference.identifier

        self.assertIsNone(session.get('omics_units', None))

        response = self.client.post(self.url, {
            'omics_units': omics_unit_id,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            self.client.session.get('omics_units'),
            [omics_unit_id]
        )
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=1
        )
        self.assertContains(
            response,
            'Download a CSV file with the selected Pixels'
        )

    def test_select_unknown_pixels(self):

        session = self.client.session

        self.assertIsNone(session.get('omics_units', None))

        response = self.client.post(self.url, {
            'omics_units': 'invalid',
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            self.client.session.get('omics_units'),
            ['invalid']
        )
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=0
        )
        self.assertNotContains(
            response,
            'Download a CSV file with the selected Pixels'
        )

    def test_select_subset_of_pixels(self):

        session = self.client.session
        omics_unit_id_1 = self.pixels[0].omics_unit.reference.identifier
        omics_unit_id_2 = self.pixels[1].omics_unit.reference.identifier

        self.assertIsNone(session.get('omics_units', None))

        response = self.client.post(self.url, {
            'omics_units': f'{omics_unit_id_1}, {omics_unit_id_2}',
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            set(self.client.session.get('omics_units')),
            set([omics_unit_id_1, omics_unit_id_2])
        )
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=2
        )

    def test_empty_subset_returns_all_pixels(self):

        session = self.client.session
        self.assertIsNone(session.get('omics_units', None))

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertIsNone(session.get('omics_units'))
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=self.n_pixels
        )


class PixelSetExportPixelsViewTestCase(CoreFixturesTestCase):

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

        self.pixel_set = factories.PixelSetFactory()
        self.pixel_set.analysis.experiments.add(
            factories.ExperimentFactory()
        )
        factories.PixelFactory.create_batch(
            10,
            pixel_set=self.pixel_set
        )

        self.url = self.pixel_set.get_export_pixels_url()

    def test_returns_csv_file(self):

        fake_dt = timezone.make_aware(datetime.datetime(2018, 1, 12, 11, 00))

        with patch.object(timezone, 'now', return_value=fake_dt):

            response = self.client.get(self.url)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')
            self.assertEqual(
                response['Content-Disposition'],
                'attachment; filename={}'.format(
                    PixelSetExportPixelsView.get_export_archive_filename()
                )
            )
            self.assertContains(response, 'Omics Unit,Value,QS')

    def test_get_export_archive_filename(self):

        fake_dt = timezone.make_aware(datetime.datetime(2018, 1, 12, 11, 00))

        with patch.object(timezone, 'now', return_value=fake_dt):
            self.assertEqual(
                PixelSetExportPixelsView.get_export_archive_filename(),
                'pixels_20180112_11h00m00s.csv'
            )
