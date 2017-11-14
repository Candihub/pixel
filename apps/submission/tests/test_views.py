from pathlib import PurePath
from tempfile import mkdtemp

import pytest
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext as _
from openpyxl import load_workbook

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from apps.submission.io.xlsx import (
    sha256_checksum, generate_template, get_template_version
)


class LoginRequiredTestMixin(object):
    """
    A mixin to test views with the login_required decorator.

    Nota bene: you must at least define an url property
    """

    method = 'get'
    template = None
    url = None

    def setUp(self):
        """Create simple user (not staff nor superuser)"""
        self.simple_user = PixelerFactory(
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

    def login(self):
        """User login shortcut"""
        return self.client.login(
            username=self.simple_user.username,
            password=PIXELER_PASSWORD,
        )

    def test_login_required(self):

        if self.url is None:
            raise NotImplementedError(
                _(
                    "You should define an url when your TestCase inherits from"
                    " the LoginRequiredTestCase"
                )
            )

        # User is not logged in, she should be redirected to the login form
        response = self.client.get(self.url)
        expected_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertRedirects(response, expected_url)

        # Log an active user in and then test we are not redirected
        self.assertTrue(self.login())

        response = eval('self.client.{}(self.url)'.format(self.method))
        self.assertEqual(response.status_code, 200)

        if self.template is not None:
            self.assertTemplateUsed(response, self.template)


class LoginRequiredMixinTestCase(TestCase):

    def test_declaring_url_attribute_is_mandatory(self):

        class FooViewTestCase(LoginRequiredTestMixin):
            pass

        foo = FooViewTestCase()

        with pytest.raises(NotImplementedError):
            foo.test_login_required()


class DownloadXLSXTemplateViewTestCase(LoginRequiredTestMixin, TestCase):

    url = reverse('submission:download')
    template = 'submission/download_xlsx_template.html'

    def test_context_data(self):

        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.context.get('step'), 'download')
        self.assertEqual(response.context.get('next_step_url'), '#')
        self.assertEqual(response.context.get('check'), False)

    def test_context_data_with_check_param(self):

        self.login()
        url = '{}?check=true'.format(self.url)
        response = self.client.get(url)

        self.assertEqual(response.context.get('check'), True)
        self.assertEqual(response.context.get('version'), None)
        self.assertEqual(response.context.get('checksum'), None)

    def test_context_data_after_download(self):

        self.login()

        download_url = reverse('submission:generate_template')
        self.client.post(download_url)

        response = self.client.get(self.url)

        self.assertEqual(response.context.get('check'), False)
        self.assertEqual(
            response.context.get('version'),
            self.client.session['template']['version']
        )
        self.assertEqual(
            response.context.get('checksum'),
            self.client.session['template']['checksum']
        )
        self.assertContains(
            response,
            '<a href="?check=true" class="action secondary">',
        )

    def test_context_data_after_download_with_check_param(self):

        self.login()

        download_url = reverse('submission:generate_template')
        self.client.post(download_url)

        url = '{}?check=true'.format(self.url)
        response = self.client.get(url)

        self.assertContains(
            response,
            '<code>{}</code>'.format(
                self.client.session['template']['version']
            ),
        )
        self.assertContains(
            response,
            '<code>{}</code>'.format(
                self.client.session['template']['checksum']
            ),
        )


class GenerateXLSXTemplateViewTestCase(LoginRequiredTestMixin, TestCase):

    method = 'post'
    url = reverse('submission:generate_template')

    def test_post(self):

        self.login()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

        template_path = PurePath(mkdtemp(), 'meta.xlsx')
        _, expected_version = generate_template(template_path)

        self.assertEqual(
            response.get('Content-Disposition'),
            'attachment; filename="{}"'.format(
                '{}-{}.xlsx'.format(
                    template_path.stem,
                    expected_version[:8]
                )
            )
        )

        expected_content_type = (
            'application/vnd'
            '.openxmlformats-officedocument'
            '.spreadsheetml'
            '.sheet'
        )
        self.assertEqual(
            response.get('Content-Type'),
            expected_content_type
        )

    def test_generated_file(self):

        self.login()
        response = self.client.post(self.url)

        # Write generated file
        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        with open(template_path, 'wb') as template_file:
            template_file.write(response.content)

        expected_checksum = sha256_checksum(template_path)
        expected_version = get_template_version(template_path)

        self.assertEqual(
            self.client.session['template']['checksum'],
            expected_checksum
        )

        self.assertEqual(
            self.client.session['template']['version'],
            expected_version
        )

        # Try to open it as an excel workbook and smoke test it
        wb = load_workbook(template_path)
        ws = wb.active
        self.assertEqual(ws.title, 'Import information for Pixel')
