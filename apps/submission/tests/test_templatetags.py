from django.test import TestCase
from django.urls import reverse

from .test_views import ValidateTestMixin
from ..models import SubmissionProcess
from ..templatetags.submission import hide_traceback, core_tasks


class HideTracebackFilterTestCase(TestCase):

    def test_with_expected_error_and_traceback(self):

        value = (
            'Unexpected foo error\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        expected = 'Unexpected foo error'
        self.assertEqual(hide_traceback(value), expected)

    def test_with_more_error_rows(self):

        value = (
            'Unexpected foo error\n'
            'Another row\n'
            'Traceback (most recent call last):\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        expected = 'Unexpected foo error\nAnother row'
        self.assertEqual(hide_traceback(value), expected)

    def test_without_traceback(self):

        value = (
            'Unexpected foo error\n'
            'Another row\n'
            '  File "<stdin>", line 1, in <module>\n'
            '  NameError: name \'a\' is not defined\n'
        )
        self.assertEqual(hide_traceback(value), value)


class CoreTasksFilterTestCase(ValidateTestMixin, TestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    def setUp(self):

        super().setUp()

        task = self.process.task_set.first()
        params = {
            'process_pk': self.process.pk,
            'task_pk': task.pk,
        }
        url = reverse('submission:validation', kwargs=params)
        self.client.post(
            url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )

    def test_filtering(self):

        process = SubmissionProcess.objects.get()
        tasks = process.task_set.all().reverse()
        expected = (
            'download',
            'upload',
            'meta',
            'validation'
        )
        self.assertEqual(
            tuple(str(t.flow_task).lower() for t in core_tasks(tasks)),
            expected
        )
