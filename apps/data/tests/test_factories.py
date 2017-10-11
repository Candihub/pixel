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


class EntryFactoryTestCase(TestCase):

    def test_can_create_entry(self):

        entry_qs = models.Entry.objects.all()
        repository_qs = models.Repository.objects.all()

        self.assertEqual(entry_qs.count(), 0)
        self.assertEqual(repository_qs.count(), 0)

        entry = factories.EntryFactory()

        self.assertGreater(len(entry.identifier), 1)
        self.assertGreater(len(entry.description), 1)
        self.assertGreater(len(entry.url), 1)
        self.assertGreater(len(entry.repository.name), 1)
        self.assertEqual(entry_qs.count(), 1)
        self.assertEqual(repository_qs.count(), 1)
