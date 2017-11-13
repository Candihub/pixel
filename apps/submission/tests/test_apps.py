from django.apps import apps
from django.test import TestCase

from ..apps import SubmissionConfig


class SubmissionConfigTestCase(TestCase):

    def test_config(self):

        expected = 'submission'
        self.assertEqual(SubmissionConfig.name, expected)

        expected = 'apps.submission'
        self.assertEqual(apps.get_app_config('submission').name, expected)
