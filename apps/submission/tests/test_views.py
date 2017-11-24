from pathlib import PurePath
from tempfile import mkdtemp

from django.test import TestCase
from django.urls import reverse
from openpyxl import load_workbook

from apps.submission.io.xlsx import (
    sha256_checksum, generate_template, get_template_version
)


class DownloadXLSXTemplateViewTestCase(TestCase):

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

    def test_context_data_with_check_param_but_no_prior_download(self):

        self.login()
        url = '{}?check=true'.format(self.url)
        response = self.client.get(url)

        self.assertContains(
            response,
            """
                <div class="message warning">
                Download the meta.xlsx template first. Then you will be able
                to display its checksum.
                </div>
            """,
            html=True
        )
        self.assertContains(
            response,
            '<a href="?check=true" class="action secondary">',
        )
        self.assertNotContains(
            response,
            """
            <div class="checksum">
            <table>
              <tbody>
                <tr>
                  <th>
                    version
                  </th>
                  <td>
            """,
            html=True
        )

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


class GenerateXLSXTemplateViewTestCase(TestCase):

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
