from django.test import TestCase
from django.urls import reverse

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory


class RegistrationTestCase(TestCase):

    def setUp(self):

        self.user = PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def test_login(self):

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        response = self.client.post(
            self.login_url,
            data={
                'username': self.user.username,
                'password': PIXELER_PASSWORD,
            }
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            self.login_url,
            data={
                'username': self.user.username,
                'password': PIXELER_PASSWORD,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_login_with_wrong_credentials(self):

        fake_password = 'Foo42'
        response = self.client.post(
            self.login_url,
            data={
                'username': self.user.username,
                'password': fake_password,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        response = self.client.post(
            self.login_url,
            data={
                'username': self.user.username,
                'password': fake_password,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_with_non_staff_user(self):

        non_staff_user = PixelerFactory(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        response = self.client.post(
            self.login_url,
            data={
                'username': non_staff_user.username,
                'password': PIXELER_PASSWORD,
            }
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            self.login_url,
            data={
                'username': non_staff_user.username,
                'password': PIXELER_PASSWORD,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_login_with_inactive_user(self):

        inactive_user = PixelerFactory(
            is_active=False,
            is_staff=False,
            is_superuser=False,
        )

        response = self.client.post(
            self.login_url,
            data={
                'username': inactive_user.username,
                'password': PIXELER_PASSWORD,
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

        response = self.client.post(
            self.login_url,
            data={
                'username': inactive_user.username,
                'password': PIXELER_PASSWORD,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_logout(self):

        self.client.login(
            username=self.user.username,
            password=PIXELER_PASSWORD,
        )

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/logged_out.html')
