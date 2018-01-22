from django.apps import apps
from django.test import TestCase

from ..apps import ExplorerConfig


class ExplorerConfigTestCase(TestCase):

    def test_config(self):

        expected = 'explorer'
        self.assertEqual(ExplorerConfig.name, expected)

        expected = 'apps.explorer'
        self.assertEqual(apps.get_app_config('explorer').name, expected)
