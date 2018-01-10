from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from .. import models
from .test_views import AsyncImportMixin, ValidateTestMixin


class SubmissionProcessTestCase(TestCase):

    def test_can_create_submission_process(self):

        label = 'Candida datasest 0001'

        qs = models.SubmissionProcess.objects.all()
        self.assertEqual(qs.count(), 0)

        process = models.SubmissionProcess.objects.create(
            label=label,
        )

        self.assertEqual(process.label, label)
        self.assertEqual(qs.count(), 1)

    def test_archive_upload_to(self):

        # Create process and activate tasks
        self.user = PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=self.user.username,
            password=PIXELER_PASSWORD,
        )
        self.client.post(
            reverse('submission:start'),
            data={
                'label': 'Candida datasest 0001',
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )

        process = models.SubmissionProcess.objects.get()
        filename = 'archive.zip'
        upload_path = models.SubmissionProcess.archive_upload_to(
            process,
            filename
        )
        expected = '{}/submissions/{}/{}'.format(
            process.created_by.id,
            process.id,
            filename
        )

        self.assertEqual(upload_path, expected)


class SubmissionProcessIsDoneHelperTestCase(ValidateTestMixin,
                                            AsyncImportMixin,
                                            TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/data/fixtures/test_entries.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_is_done(self):

        self.assertFalse(self.process.is_done)

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self._wait_for_async_import(self.process)

        self.process.refresh_from_db()
        self.assertTrue(self.process.is_done)


class SubmissionProcessIsFailedHelperTestCase(ValidateTestMixin,
                                              AsyncImportMixin,
                                              TransactionTestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    # Forcing data serialization is also required
    serialized_rollback = True

    def test_is_failed(self):

        self.assertFalse(self.process.is_failed)

        response = self.client.post(
            self.url,
            data={
                '_viewflow_activation-started': '2000-01-01',
                'validated': True,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        self._wait_for_async_import(self.process)

        self.process.refresh_from_db()
        self.assertTrue(self.process.is_failed)
