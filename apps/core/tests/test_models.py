from django.test import TestCase

from apps.data.factories import EntryFactory
from .. import models


class SpeciesTestCase(TestCase):

    def test_can_create_species(self):

        name = 'Saccharomyces cerevisiae'
        reference = EntryFactory()
        description = 'lorem ipsum'

        qs = models.Species.objects.all()
        self.assertEqual(qs.count(), 0)

        species = models.Species.objects.create(
            name=name,
            reference=reference,
            description=description,
        )

        self.assertEqual(species.name, name)
        self.assertEqual(species.reference.id, reference.id)
        self.assertEqual(species.description, description)
        self.assertEqual(qs.count(), 1)

    def test_can_create_species_without_description(self):

        name = 'Saccharomyces cerevisiae'
        reference = EntryFactory()

        qs = models.Species.objects.all()
        self.assertEqual(qs.count(), 0)

        species = models.Species.objects.create(
            name=name,
            reference=reference,
        )

        self.assertEqual(species.name, name)
        self.assertEqual(species.reference.id, reference.id)
        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):

        name = 'Saccharomyces cerevisiae'
        reference = EntryFactory()

        species = models.Species.objects.create(
            name=name,
            reference=reference,
        )

        self.assertEqual(str(species), name)
