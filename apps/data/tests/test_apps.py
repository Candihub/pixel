from django.apps import apps
from django.test import TestCase

from ..apps import DataConfig


class DataConfigTestCase(TestCase):

    def test_config(self):

        expected = 'data'
        self.assertEqual(DataConfig.name, expected)

        expected = 'apps.data'
        self.assertEqual(apps.get_app_config('data').name, expected)
