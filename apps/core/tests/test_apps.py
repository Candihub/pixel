from django.apps import apps
from django.test import TestCase

from ..apps import CoreConfig


class CoreConfigTestCase(TestCase):

    def test_config(self):

        expected = 'core'
        self.assertEqual(CoreConfig.name, expected)

        expected = 'apps.core'
        self.assertEqual(apps.get_app_config('core').name, expected)
