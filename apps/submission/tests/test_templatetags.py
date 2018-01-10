from pathlib import Path

from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from ..models import SubmissionProcess
from ..templatetags import submission
from .io.test_pixel import LoadCGDMixin
from .test_views import AsyncImportMixin, StartTestMixin, ValidateTestMixin


class HideTracebackFilterTestCase(TestCase):

    def test_with_expected_error_and_traceback(self):

        value = (
            'Unexpected foo error\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        expected = 'Unexpected foo error'
        self.assertEqual(submission.hide_traceback(value), expected)

    def test_with_more_error_rows(self):

        value = (
            'Unexpected foo error\n'
            'Another row\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        expected = 'Unexpected foo error\nAnother row'
        self.assertEqual(submission.hide_traceback(value), expected)

    def test_without_traceback(self):

        value = (
            'Unexpected foo error\n'
            'Another row\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        self.assertEqual(submission.hide_traceback(value), value)


class CoreTasksFilterTestCase(ValidateTestMixin,
                              AsyncImportMixin,
                              TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def setUp(self):

        super().setUp()

        self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )

        self._wait_for_async_import(self.process)

    def test_filtering(self):

        tasks = self.process.task_set.all().reverse()
        expected = (
            'download',
            'upload',
            'meta',
            'validation',
            'import archive'
        )
        tasks = tuple(
            str(t.flow_task).lower() for t in submission.core_tasks(tasks)
        )
        self.assertEqual(
            tasks,
            expected
        )


class SubmissionRatioTestCase(StartTestMixin,
                              AsyncImportMixin,
                              LoadCGDMixin,
                              TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_submission_ratio_along_process(self):

        # Start
        self.client.post(
            reverse('submission:start'),
            data={
                'label': 'Candida datasest 0001',
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )
        process = SubmissionProcess.objects.get()
        task = process.task_set.first()
        self.assertEqual(
            submission.submission_ratio(process),
            8
        )

        # Download
        url = reverse(
            'submission:download',
            kwargs={
                'process_pk': process.pk,
                'task_pk': task.pk,
            }
        )
        self.client.post(
            url,
            data={
                '_viewflow_activation-started': '2000-01-01',
            }
        )
        self.assertEqual(
            submission.submission_ratio(process),
            25
        )

        # Upload
        task = process.task_set.first()
        archive = Path('apps/submission/fixtures/dataset-0001-shrink.zip')
        url = reverse(
            'submission:upload',
            kwargs={
                'process_pk': process.pk,
                'task_pk': task.pk,
            }
        )
        with archive.open('rb') as archive_file:
            self.client.post(
                url,
                data={
                    '_viewflow_activation-started': '2000-01-01',
                    'archive': archive_file,
                },
                follow=True,
            )
        self.assertEqual(
            submission.submission_ratio(process),
            58
        )

        # Validate
        self._load_cgd_entries()
        task = process.task_set.first()
        url = reverse(
            'submission:validation',
            kwargs={
                'process_pk': process.pk,
                'task_pk': task.pk,
            }
        )
        self.client.post(
            url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )
        self.assertEqual(
            submission.submission_ratio(process),
            75
        )

        self._wait_for_async_import(process)
        self.assertEqual(
            submission.submission_ratio(process),
            100
        )
