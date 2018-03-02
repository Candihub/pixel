from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.core import factories


class ContactViewTestCase(TestCase):

    def setUp(self):

        self.url = reverse('core:home')

    def test_renders_the_home_view(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_renders_the_home_authenticated_view_when_connected(self):

        self.user = factories.PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=self.user.username,
            password=factories.PIXELER_PASSWORD,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home-authenticated.html')
