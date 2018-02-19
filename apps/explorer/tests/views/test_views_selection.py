import json
import pytest

from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.core import factories
from apps.core.tests import CoreFixturesTestCase
from apps.explorer.views import DataTableCumulativeView, DataTableSelectionView
from apps.explorer.views.views_selection import GetSearchTermsMixin


class PixelSetSelectionViewTestCase(CoreFixturesTestCase):

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
        self.url = reverse('explorer:pixelset_selection')

    def test_redirects_to_list_view_when_invalid(self):

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('explorer:pixelset_list'))

    def test_displays_message_after_redirect_when_selection_is_empty(self):

        response = self.client.get(self.url, follow=True)

        self.assertContains(
            response,
            (
                '<div class="message error">'
                'Cannot explore an empty selection.'
                '</div>'
            ),
            html=True
        )

    def test_renders_pixelset_selection_template(self):

        # select 2 pixel sets
        pixel_sets = factories.PixelSetFactory.create_batch(2)
        data = {
            'pixel_sets': [str(p.id) for p in pixel_sets]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explorer/pixelset_selection.html')

        self.assertContains(
            response,
            '<title>Pixel Sets - Your selection</title>'
        )

        self.assertContains(
            response,
            '<div class="pixelset-item">',
            count=len(pixel_sets)
        )

    def test_renders_distributions_for_each_pixel_set(self):

        # select 2 pixel sets
        pixel_sets = factories.PixelSetFactory.create_batch(2)
        data = {
            'pixel_sets': [str(p.id) for p in pixel_sets]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # cumulative distributions
        self.assertContains(
            response,
            f'<div class="histogram" id="values-histogram">'
        )
        self.assertContains(
            response,
            f'<div class="histogram" id="scores-histogram">'
        )

        self.assertContains(
            response,
            f'<div class="histogram" id="values-histogram-{pixel_sets[0].id}">'
        )
        self.assertContains(
            response,
            f'<div class="histogram" id="scores-histogram-{pixel_sets[0].id}">'
        )

        self.assertContains(
            response,
            f'<div class="histogram" id="values-histogram-{pixel_sets[1].id}">'
        )
        self.assertContains(
            response,
            f'<div class="histogram" id="scores-histogram-{pixel_sets[1].id}">'
        )


class DataTableSelectionViewTestCase(TestCase):

    def test_get_headers_must_be_implemented(self):

        class DataTableSelectionViewWithNoGetHeaders(DataTableSelectionView):
            pass

        with pytest.raises(NotImplementedError):
            view = DataTableSelectionViewWithNoGetHeaders()
            view.get_headers()


class PixelSetSelectionValuesViewTestCase(GetSearchTermsMixin,
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
            'explorer:pixelset_selection_values',
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

    def test_filters_by_omics_units(self):

        session = self.client.session

        # select pixel set, otherwise we cannot set omics units
        self.client.post(
            reverse('explorer:pixelset_select'),
            {'pixel_sets': [self.pixel_set.id]},
            follow=True
        )
        response = self.client.get(self.url)

        self.assertIsNone(self.get_search_terms(session, default=None))

        selected_pixel = self.pixels[0]

        # set search terms in session
        response = self.client.post(reverse('explorer:pixelset_selection'), {
            'search_terms': selected_pixel.omics_unit.reference.identifier,
        }, follow=True)

        self.assertRedirects(response, reverse('explorer:pixelset_selection'))

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

    def test_filters_by_term_in_description(self):

        session = self.client.session

        # select pixel set, otherwise we cannot set omics units
        self.client.post(
            reverse('explorer:pixelset_select'),
            {'pixel_sets': [self.pixel_set.id]},
            follow=True
        )
        response = self.client.get(self.url)

        self.assertIsNone(self.get_search_terms(session, default=None))

        selected_pixel = self.pixels[0]

        description = selected_pixel.omics_unit.reference.description
        first_word = description.split(' ')[0]

        # set search terms in session
        response = self.client.post(reverse('explorer:pixelset_selection'), {
            'search_terms': first_word,
        }, follow=True)

        self.assertRedirects(response, reverse('explorer:pixelset_selection'))

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


class PixelSetSelectionQualityScoresViewTestCase(GetSearchTermsMixin,
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
            'explorer:pixelset_selection_quality_scores',
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

        # select pixel set, otherwise we cannot set omics units
        self.client.post(
            reverse('explorer:pixelset_select'),
            {'pixel_sets': [self.pixel_set.id]},
            follow=True
        )
        response = self.client.get(self.url)

        self.assertIsNone(self.get_search_terms(session, default=None))

        selected_pixel = self.pixels[0]

        # set search terms in session
        response = self.client.post(reverse('explorer:pixelset_selection'), {
            'search_terms': selected_pixel.omics_unit.reference.identifier,
        }, follow=True)

        self.assertRedirects(response, reverse('explorer:pixelset_selection'))

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

        # select pixel set, otherwise we cannot set omics units
        self.client.post(
            reverse('explorer:pixelset_select'),
            {'pixel_sets': [self.pixel_set.id]},
            follow=True
        )
        response = self.client.get(self.url)

        self.assertIsNone(self.get_search_terms(session, default=None))

        selected_pixel = self.pixels[0]

        description = selected_pixel.omics_unit.reference.description
        first_word = description.split(' ')[0]

        # set search terms in session
        response = self.client.post(reverse('explorer:pixelset_selection'), {
            'search_terms': first_word,
        }, follow=True)

        self.assertRedirects(response, reverse('explorer:pixelset_selection'))

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


class DataTableCumulativeViewTestCase(TestCase):

    def test_get_headers_must_be_implemented(self):

        class DataTableCumulativeViewWithNoGetHeaders(DataTableCumulativeView):
            pass

        with pytest.raises(NotImplementedError):
            view = DataTableCumulativeViewWithNoGetHeaders()
            view.get_headers()


class PixelSetSelectionCumulativeQualityScoresViewTestCase(CoreFixturesTestCase):  # noqa

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
            'explorer:pixelset_selection_cumulative_quality_scores'
        )

    def test_returns_bad_request_when_not_ajax(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)

    def test_returns_json(self):

        # select 1 pixel set
        data = {
            'pixel_sets': [self.pixel_set.id]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

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

    def test_no_selected_pixel_sets_returns_empty(self):

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
        self.assertEqual(len(rows), 0)


class PixelSetSelectionCumulativeValuesViewTestCase(CoreFixturesTestCase):

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

        self.url = reverse('explorer:pixelset_selection_cumulative_values')

    def test_returns_bad_request_when_not_ajax(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)

    def test_returns_json(self):

        # select 1 pixel set
        data = {
            'pixel_sets': [self.pixel_set.id]
        }
        self.client.post(
            reverse('explorer:pixelset_select'), data, follow=True
        )

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

    def test_no_selected_pixel_sets_returns_empty(self):

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
        self.assertEqual(len(rows), 0)
