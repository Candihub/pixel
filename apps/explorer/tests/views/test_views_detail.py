import datetime
import json
import pytest

from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as date_filter
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from apps.core import factories, models
from apps.core.tests import CoreFixturesTestCase
from apps.explorer.views import (
    PixelSetDetailView, PixelSetExportPixelsView, DataTableDetailView,
)
from apps.explorer.views.views_detail import GetSearchTermsMixin


class PixelSetDetailViewTestCase(GetSearchTermsMixin, CoreFixturesTestCase):

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
        title = 'Edit this Pixel Set from the admin'
        expected = (
            f'<a href="{admin_url}" title="{title}" class="edit">'
            '<i class="fa fa-pencil" aria-hidden="true"></i>'
            'Edit this Pixel Set'
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
        title = 'Edit this Pixel Set from the admin'
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

        pixel_set = models.PixelSet.objects.get()

        expected = (
            '<span class="completed-at">'
            'Completion date: {}'
            '</span>'
        )
        self.assertContains(
            response,
            expected.format(
                date_filter(pixel_set.analysis.completed_at)
            ),
            count=1,
            html=True
        )
        self.assertContains(
            response,
            expected.format(
                date_filter(
                    pixel_set.analysis.experiments.get().completed_at
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

        self.assertIsNone(self.get_search_terms(session, default=None))

        response = self.client.post(self.url, {
            'search_terms': omics_unit_id,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            self.get_search_terms(self.client.session),
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

        self.assertIsNone(self.get_search_terms(session, default=None))

        response = self.client.post(self.url, {
            'search_terms': 'invalid',
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            self.get_search_terms(self.client.session),
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

        self.assertIsNone(self.get_search_terms(session, default=None))

        response = self.client.post(self.url, {
            'search_terms': f'{omics_unit_id_1}, {omics_unit_id_2}',
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertEqual(
            set(self.get_search_terms(self.client.session)),
            set([omics_unit_id_1, omics_unit_id_2])
        )
        self.assertContains(
            response,
            '<tr class="pixel">',
            count=2
        )

    def test_empty_subset_returns_all_pixels(self):

        session = self.client.session
        self.assertIsNone(self.get_search_terms(session, default=None))

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())
        self.assertIsNone(self.get_search_terms(session, default=None))
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


class PixelSetDetailValuesViewTestCase(GetSearchTermsMixin,
                                       CoreFixturesTestCase):

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
        self.pixels = factories.PixelFactory.create_batch(
            2,
            pixel_set=self.pixel_set
        )

        self.url = reverse(
            'explorer:pixelset_detail_values',
            kwargs={'pk': str(self.pixel_set.id)}
        )

    def test_returns_bad_request_when_not_ajax(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)

    def test_returns_json(self):

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'value')

        rows = data['rows']
        self.assertEqual(len(rows), 2)

    def test_filters_by_term_in_description(self):

        session = self.client.session

        selected_pixel = self.pixels[0]

        description = selected_pixel.omics_unit.reference.description
        first_words = description.split(' ')[0:2]

        self.assertIsNone(self.get_search_terms(session, default=None))

        # set search terms in session
        response = self.client.post(self.pixel_set.get_absolute_url(), {
            'search_terms': first_words,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'value')

        rows = data['rows']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['c'][0]['v'], str(selected_pixel.id))
        self.assertEqual(rows[0]['c'][1]['v'], selected_pixel.value)

    def test_filters_by_(self):

        session = self.client.session
        selected_pixel = self.pixels[0]

        self.assertIsNone(self.get_search_terms(session, default=None))

        # set search terms in session
        response = self.client.post(self.pixel_set.get_absolute_url(), {
            'search_terms': selected_pixel.omics_unit.reference.identifier,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'value')

        rows = data['rows']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['c'][0]['v'], str(selected_pixel.id))
        self.assertEqual(rows[0]['c'][1]['v'], selected_pixel.value)


class PixelSetDetailQualityScoresViewTestCase(GetSearchTermsMixin,
                                              CoreFixturesTestCase):

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
        self.pixels = factories.PixelFactory.create_batch(
            2,
            pixel_set=self.pixel_set
        )

        self.url = reverse(
            'explorer:pixelset_detail_quality_scores',
            kwargs={'pk': str(self.pixel_set.id)}
        )

    def test_returns_bad_request_when_not_ajax(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)

    def test_returns_json(self):

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'quality_score')

        rows = data['rows']
        self.assertEqual(len(rows), 2)

    def test_filters_by_omics_units(self):

        session = self.client.session
        selected_pixel = self.pixels[0]

        self.assertIsNone(self.get_search_terms(session, default=None))

        # set search terms in session
        response = self.client.post(self.pixel_set.get_absolute_url(), {
            'search_terms': selected_pixel.omics_unit.reference.identifier,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'quality_score')

        rows = data['rows']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['c'][0]['v'], str(selected_pixel.id))
        self.assertEqual(rows[0]['c'][1]['v'], selected_pixel.quality_score)

    def test_filters_by_term_in_description(self):

        session = self.client.session

        selected_pixel = self.pixels[0]

        description = selected_pixel.omics_unit.reference.description
        first_words = description.split(' ')[0:2]

        self.assertIsNone(self.get_search_terms(session, default=None))

        # set search terms in session
        response = self.client.post(self.pixel_set.get_absolute_url(), {
            'search_terms': first_words,
        }, follow=True)

        self.assertRedirects(response, self.pixel_set.get_absolute_url())

        response = self.client.get(
            self.url,
            data={},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = json.loads(response.content)

        cols = data['cols']
        self.assertEqual(cols[0]['label'], 'id')
        self.assertEqual(cols[1]['label'], 'quality_score')

        rows = data['rows']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['c'][0]['v'], str(selected_pixel.id))
        self.assertEqual(rows[0]['c'][1]['v'], selected_pixel.quality_score)


class DataTableDetailViewTestCase(TestCase):

    def test_get_headers_must_be_implemented(self):

        class DataTableDetailViewWithNoGetHeaders(DataTableDetailView):
            pass

        with pytest.raises(NotImplementedError):
            view = DataTableDetailViewWithNoGetHeaders()
            view.get_headers()


class PixelSetDetailClearViewTestCase(GetSearchTermsMixin,
                                      CoreFixturesTestCase):

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
        self.pixels = factories.PixelFactory.create_batch(
            2,
            pixel_set=self.pixel_set
        )
        self.url = self.pixel_set.get_absolute_url()

    def test_clear_search_terms_in_session(self):

        session = self.client.session
        omics_unit_id = self.pixels[0].omics_unit.reference.identifier

        self.assertIsNone(self.get_search_terms(session, default=None))

        response = self.client.post(self.url, {
            'search_terms': omics_unit_id,
        }, follow=True)

        self.assertEqual(
            self.get_search_terms(self.client.session, default=None),
            [omics_unit_id]
        )

        # no let's clear the search terms
        response = self.client.post(
            reverse(
                'explorer:pixelset_detail_clear',
                kwargs={'pk': str(self.pixel_set.id)}
            )
        )

        self.assertRedirects(response, self.url)
        self.assertEqual(
            self.get_search_terms(self.client.session, default=None),
            []
        )
