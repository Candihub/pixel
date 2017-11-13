from django.test import TestCase
from django.urls import reverse

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory


class DownloadXLSXTemplateViewTestCase(TestCase):

    def setUp(self):

        self.url = reverse('submission:download')
        self.template = 'submission/download_xlsx_template.html'
        self.simple_user = PixelerFactory(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

    def test_login_required(self):

        # User is not logged in, she should be redirected to the login form
        response = self.client.get(self.url)
        expected_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertRedirects(response, expected_url)

        # Log an active user in and then test we are not redirected
        self.assertTrue(
            self.client.login(
                username=self.simple_user.username,
                password=PIXELER_PASSWORD,
            )
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_context_data(self):

        self.assertTrue(
            self.client.login(
                username=self.simple_user.username,
                password=PIXELER_PASSWORD,
            )
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context.get('step'), 'download')
        self.assertEqual(response.context.get('next_step_url'), '#')
