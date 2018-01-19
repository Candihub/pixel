import logging

from pathlib import Path, PurePath
from tempfile import mkdtemp
from time import sleep
from unittest.mock import patch

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from openpyxl import load_workbook
from viewflow.activation import STATUS
from viewflow.base import Flow

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from apps.core.models import Tag
from apps.core.tests import CoreFixturesTestCase
from ..flows import SubmissionFlow
from ..io.archive import PixelArchive
from ..io.xlsx import (
    sha256_checksum, generate_template, get_template_version
)
from ..models import SubmissionProcess
from ..views import NextTaskRedirectView

logger = logging.getLogger(__name__)


class StartTestMixin(object):

    def setUp(self):

        self.user = PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=self.user.username,
            password=PIXELER_PASSWORD,
        )


class DownloadTestMixin(StartTestMixin):

    def setUp(self):

        super().setUp()

        self.client.post(
            reverse('submission:start'),
            data={
                'label': 'Candida datasest 0001',
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )

        self.process = SubmissionProcess.objects.get()
        self.task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': self.task.pk,
        }
        self.url = reverse('submission:download', kwargs=params)


class UploadTestMixin(DownloadTestMixin):

    def setUp(self):

        super().setUp()

        task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': task.pk,
        }
        download_url = reverse('submission:download', kwargs=params)
        self.client.post(
            download_url,
            data={
                '_viewflow_activation-started': '2000-01-01',
            }
        )

        self.task = self.process.task_set.first()
        params.update({'task_pk': self.task.pk})
        self.url = reverse('submission:upload', kwargs=params)

        self.archive = Path('apps/submission/fixtures/dataset-0001-shrink.zip')


class ValidateTestMixin(UploadTestMixin):

    def setUp(self):

        super().setUp()

        task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': task.pk,
        }
        upload_url = reverse('submission:upload', kwargs=params)
        with self.archive.open('rb') as archive_file:
            self.client.post(
                upload_url,
                data={
                    '_viewflow_activation-started': '2000-01-01',
                    'archive': archive_file,
                },
                follow=True,
            )

        self.task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': self.task.pk,
        }
        self.url = reverse('submission:validation', kwargs=params)


class TagsTestMixin(ValidateTestMixin):

    def setUp(self):

        super().setUp()

        # Create tags
        tags = (
            'complex/molecule/atom',
            'omics/rna',
            'omics/dna',
            'omics/protein',
            'msms',
        )
        for tag in tags:
            Tag.objects.create(name=tag)

        self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )

        self.task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': self.task.pk,
        }
        self.url = reverse('submission:tags', kwargs=params)


class AsyncImportMixin(object):

    def _wait_for_async_import(self, process, timeout=60):

        for t in range(timeout):
            process.refresh_from_db()
            latest_task = process.task_set.all()[0]
            logging.debug('{:04d} sec — status:{} imported:{} Task:{}'.format(
                t, process.status, process.imported, latest_task
            ))
            if latest_task.status == STATUS.ERROR:
                return
            if process.status == STATUS.DONE:
                break
            sleep(1)

        if process.imported is False:
            raise TimeoutError(
                'Importation timed out (> {}s)'.format(timeout)
            )


class NextTaskRedirectViewTestCase(UploadTestMixin, TestCase):

    def setUp(self):

        super().setUp()

        self.url = reverse(
            'submission:next_task',
            kwargs={
                'process_pk': self.process.pk,
                'task_pk': self.task.pk,
            }
        )

        self.redirection_url = reverse(
            'submission:upload',
            kwargs={
                'process_pk': self.process.pk,
                'task_pk': self.task.pk,
            }
        )

    def test_get_process_tasks(self):

        view = NextTaskRedirectView()
        user_tasks = view.get_process_tasks(self.process, self.user)

        self.assertEqual(user_tasks.count(), 2)

    def test_get(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(self.redirection_url, 302), ]
        )

    def test_redirect_without_user_tasks(self):

        process = SubmissionProcess.objects.create(flow_class=Flow)

        url = reverse(
            'submission:next_task',
            kwargs={
                'process_pk': process.pk,
                'task_pk': 20,  # anything should be ok
            }
        )
        expected_redirection_url = reverse(
            'submission:detail',
            kwargs={
                'process_pk': process.pk,
            }
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(expected_redirection_url, 302), ]
        )

    def test_redirect_with_bad_process_task(self):

        url = reverse(
            'submission:next_task',
            kwargs={
                'process_pk': self.process.pk,
                'task_pk': 2000,
            }
        )
        expected_redirection_url = reverse(
            'submission:detail',
            kwargs={
                'process_pk': self.process.pk,
            }
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(expected_redirection_url, 302), ]
        )

    def test_next_task_from_download(self):

        task = self.process.task_set.get(flow_task=SubmissionFlow.download)
        url = reverse(
            'submission:next_task',
            kwargs={
                'process_pk': self.process.pk,
                'task_pk': task.pk,  # download
            }
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(self.redirection_url, 302), ]
        )

    def test_next_task_from_automated_task(self):

        task = self.process.task_set.get(
            flow_task=SubmissionFlow.check_download
        )
        url = reverse(
            'submission:next_task',
            kwargs={
                'process_pk': self.process.pk,
                'task_pk': task.pk,  # check_download
            }
        )
        expected_redirection_url = reverse(
            'submission:detail',
            kwargs={
                'process_pk': self.process.pk,
            }
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(expected_redirection_url, 302), ]
        )


class StartViewTestCase(StartTestMixin, TestCase):

    url = reverse('submission:start')
    template = 'submission/submission/start.html'

    def test_get_start_view(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_create_new_process(self):

        label = 'Candida datasest 0001'
        response = self.client.post(
            self.url,
            data={
                'label': label,
                '_viewflow_activation-started': '2000-01-01',
            }
        )

        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            self.url,
            data={
                'label': label,
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        expected_template = 'submission/submission/process_detail.html'
        self.assertTemplateUsed(response, expected_template)


class DownloadXLSXTemplateViewTestCase(DownloadTestMixin, TestCase):

    template = 'submission/download_xlsx_template.html'

    def test_get(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_get_context_data(self):

        response = self.client.get(self.url)
        self.assertListEqual(
            list(response.context.get('task_list')),
            list(self.process.task_set.all().order_by('created'))
        )

    def test_post(self):

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

        response = self.client.post(self.url)
        process = SubmissionProcess.objects.get()

        # Write generated file
        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        with open(template_path, 'wb') as template_file:
            template_file.write(response.content)

        expected_checksum = sha256_checksum(template_path)
        self.assertEqual(
            process.template_checksum,
            expected_checksum
        )

        expected_version = get_template_version(template_path)
        self.assertEqual(
            process.template_version,
            expected_version
        )

        # Try to open it as an excel workbook and smoke test it
        wb = load_workbook(template_path)
        ws = wb.active
        self.assertEqual(ws.title, 'Import information for Pixel')


class UploadArchiveViewTestCase(UploadTestMixin, CoreFixturesTestCase):

    template = 'submission/upload_archive.html'

    def test_get(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_post_redirection(self):

        with self.archive.open('rb') as archive_file:
            response = self.client.post(
                self.url,
                data={
                    '_viewflow_activation-started': '2000-01-01',
                    'archive': archive_file,
                }
            )
        self.assertEqual(response.status_code, 302)

    def test_uploaded_archive(self):

        with self.archive.open('rb') as archive_file:
            response = self.client.post(
                self.url,
                data={
                    '_viewflow_activation-started': '2000-01-01',
                    'archive': archive_file,
                },
                follow=True,
            )

        self.assertEqual(response.status_code, 200)

        # File name
        process = SubmissionProcess.objects.get()
        expected_name = '{}/submissions/{}/{}'.format(
            process.created_by.id,
            process.id,
            self.archive.name
        )
        self.assertEqual(process.archive.name, expected_name)

        # File size
        self.assertEqual(
            process.archive.size,
            self.archive.stat().st_size
        )


class ArchiveValidationViewTestCase(ValidateTestMixin, TestCase):
    """
    We use a TransactionTestCase to avoid using transactions for each test. By
    doing so, we commit each request allowing multiple threads to access a
    shared state of the database. This is required as the archive importation
    is a background task (using concurrent.futures).
    """

    template = 'submission/validation.html'
    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_get(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_post_redirection(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validate': True,
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_validation(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self.process.refresh_from_db()
        self.assertTrue(self.process.validated)


class TagsViewTestCase(TagsTestMixin,
                       AsyncImportMixin,
                       TransactionTestCase):

    template = 'submission/tags.html'
    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_get(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_post_redirection(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'experiment_tags': ['msms', 'omics/rna'],
                'analysis_tags': ['complex/molecule/atom', 'msms'],
                'new_analysis_tags': 'ijm, candida',
                'new_experiment_tags': 'msms/time, rna-seq',
            }
        )

        self.assertEqual(response.status_code, 302)
        self._wait_for_async_import(self.process)

    def test_tags(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'experiment_tags': ['msms', 'omics/rna'],
                'analysis_tags': ['complex/molecule/atom', 'msms'],
                'new_analysis_tags': 'ijm, candida',
                'new_experiment_tags': 'msms/time, rna-seq',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self._wait_for_async_import(self.process)

        experiment_tags = 'msms,msms/time,omics/rna,rna-seq'
        analysis_tags = 'candida,complex/molecule/atom,ijm,msms'
        expected = {
            'experiment': experiment_tags,
            'analysis': analysis_tags,
        }
        self.assertEqual(self.process.tags, expected)
        self.assertEqual(
            str(self.process.analysis.tags),
            ', '.join(analysis_tags.split(','))
        )
        self.assertEqual(
            str(self.process.analysis.experiments.get().tags),
            ', '.join(experiment_tags.split(','))
        )


class AsyncImportMixinTestCase(TagsTestMixin,
                               AsyncImportMixin,
                               TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def long_save(other, pixeler, submission=None):
        logging.debug("Calling long_save (PixelArchive.save patch)")
        sleep(5)

    @patch.object(PixelArchive, 'save', new=long_save)
    def test_raise_timeout_with_long_import_process(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(TimeoutError):
            self._wait_for_async_import(self.process, timeout=2)

        # Wait for the patched save to finish
        sleep(10)


class AsyncImportTestCase(TagsTestMixin,
                          AsyncImportMixin,
                          TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_raise_importation_error_without_entries_fixture(self):

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self._wait_for_async_import(self.process)

        latest_task = self.process.task_set.all()[0]
        self.assertEqual(latest_task.status, STATUS.ERROR)
        expected_comments = (
            'Required entries partially exists (0 vs 10). Please load entries'
            ' first thanks to the load_entries management command.'
        )
        self.assertEqual(latest_task.comments, expected_comments)
