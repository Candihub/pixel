from django.test import TestCase
from django.urls import reverse

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from .. import models


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
