from django.test import TestCase

from .. import factories, models


class RepositoryFactoryTestCase(TestCase):

    def test_can_create_repository(self):

        qs = models.Repository.objects.all()
        self.assertEqual(qs.count(), 0)

        repository = factories.RepositoryFactory()

        self.assertGreater(len(repository.name), 1)
        self.assertGreater(len(repository.url), 1)
        self.assertEqual(qs.count(), 1)
