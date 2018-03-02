from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from .. import models


class RepositoryTestCase(TestCase):

    def test_can_create_repository(self):

        name = 'Foo'
        url = 'http://foo.com'

        qs = models.Repository.objects.all()
        self.assertEqual(qs.count(), 0)

        repository = models.Repository.objects.create(
            name=name,
            url=url,
        )

        self.assertEqual(repository.name, name)
        self.assertEqual(repository.url, url)
        self.assertEqual(qs.count(), 1)

    def test_can_create_repository_without_url(self):

        name = 'Foo'

        qs = models.Repository.objects.all()
        self.assertEqual(qs.count(), 0)

        repository = models.Repository.objects.create(name=name)

        self.assertEqual(repository.name, name)
        self.assertEqual(repository.url, '')
        self.assertEqual(qs.count(), 1)

    def test_cannot_create_two_repositories_with_the_same_name(self):

        name = 'Foo'

        qs = models.Repository.objects.all()
        self.assertEqual(qs.count(), 0)

        models.Repository.objects.create(name=name)
        self.assertEqual(qs.count(), 1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                models.Repository.objects.create(name=name)

        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):

        name = 'Foo'
        repository = models.Repository.objects.create(name=name)

        self.assertEqual(str(repository), name)


class EntryTestCase(TestCase):

    def setUp(self):

        self.repository_name = 'Foo'
        self.repository_url = 'http://foo.com'
        self.repository = models.Repository.objects.create(
            name=self.repository_name,
            url=self.repository_url,
        )

    def test_can_create_entry(self):

        identifier = 'FOO001'
        description = 'lorem ipsum'
        url = 'http://foo.com/r/{}'.format(identifier)
        repository = self.repository

        qs = models.Entry.objects.all()
        self.assertEqual(qs.count(), 0)

        entry = models.Entry.objects.create(
            identifier=identifier,
            description=description,
            url=url,
            repository=repository,
        )

        self.assertEqual(entry.identifier, identifier)
        self.assertEqual(entry.description, description)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.repository.id, repository.id)
        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):

        identifier = 'FOO001'
        description = 'lorem ipsum'
        url = 'http://foo.com/r/{}'.format(identifier)
        repository = self.repository

        entry = models.Entry.objects.create(
            identifier=identifier,
            description=description,
            url=url,
            repository=repository,
        )

        self.assertEqual(str(entry), identifier)

    def test_can_create_entry_without_url(self):

        identifier = 'FOO001'
        description = 'lorem ipsum'
        repository = self.repository

        qs = models.Entry.objects.all()
        self.assertEqual(qs.count(), 0)

        entry = models.Entry.objects.create(
            identifier=identifier,
            description=description,
            repository=repository,
        )

        self.assertEqual(entry.identifier, identifier)
        self.assertEqual(entry.description, description)
        self.assertEqual(entry.url, '')
        self.assertEqual(entry.repository.id, repository.id)
        self.assertEqual(qs.count(), 1)

    def test_can_create_entry_without_identifier(self):

        identifier = 'FOO001'
        description = 'lorem ipsum'
        url = 'http://foo.com/r/{}'.format(identifier)
        repository = self.repository

        qs = models.Entry.objects.all()
        self.assertEqual(qs.count(), 0)

        entry = models.Entry.objects.create(
            description=description,
            url=url,
            repository=repository,
        )

        self.assertEqual(entry.identifier, '')
        self.assertEqual(entry.description, description)
        self.assertEqual(entry.url, url)
        self.assertEqual(entry.repository.id, repository.id)

        self.assertEqual(qs.count(), 1)

    def test_cannot_create_entry_without_identifier_or_url(self):

        description = 'lorem ipsum'
        repository = self.repository

        qs = models.Entry.objects.all()
        self.assertEqual(qs.count(), 0)

        entry = models.Entry(
            description=description,
            repository=repository,
        )

        with self.assertRaises(ValidationError):
            entry.clean()

        self.assertEqual(qs.count(), 0)
