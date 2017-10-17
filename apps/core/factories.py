from factory import Faker, Iterator, SubFactory
from factory.django import DjangoModelFactory

from apps.data.factories import EntryFactory, RepositoryFactory
from . import models


class SpeciesFactory(DjangoModelFactory):

    name = Faker('word')
    reference = SubFactory(EntryFactory)
    repository = SubFactory(RepositoryFactory)
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.Species'
        django_get_or_create = ('name', )


class StrainFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)
    species = SubFactory(SpeciesFactory)
    reference = SubFactory(EntryFactory)

    class Meta:
        model = 'core.Strain'
        django_get_or_create = ('name', )


class OmicsUnitTypeFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.OmicsUnitType'
        django_get_or_create = ('name', )


class OmicsUnitFactory(DjangoModelFactory):

    reference = SubFactory(EntryFactory)
    strain = SubFactory(StrainFactory)
    type = SubFactory(OmicsUnitTypeFactory)
    status = Iterator(s[0] for s in models.OmicsUnit.STATUS_CHOICES)

    class Meta:
        model = 'core.OmicsUnit'
        django_get_or_create = ('reference', 'strain')
