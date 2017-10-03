from django.core.urlresolvers import reverse
from django.test import TestCase


class ContactViewTestCase(TestCase):

    def setUp(self):

        self.url = reverse('core:home')

    def test_renders_the_home_view(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
