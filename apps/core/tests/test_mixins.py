from django.test import TestCase
from django.test.utils import isolate_apps

from apps.core.tests.mixins.models import ModelWithStandardID, ModelWithUUID


@isolate_apps('apps.core.tests.mixins')
class UUIDModelMixinTestCase(TestCase):

    def test_get_short_uuid(self):

        m = ModelWithUUID.objects.create()
        expected = m.id.hex[:7]

        self.assertEqual(m.get_short_uuid(), expected)

    def test_get_short_uuid_without_uuid_model(self):

        m = ModelWithStandardID.objects.create()

        with self.assertRaises(TypeError) as e:
            m.get_short_uuid()

        self.assertEqual(
            str(e.exception),
            'ModelWithStandardID model id is not a valid UUID'
        )

    def test_model_representation(self):

        m = ModelWithUUID.objects.create()
        expected = m.id.hex[:7]

        self.assertEqual(str(m), expected)
