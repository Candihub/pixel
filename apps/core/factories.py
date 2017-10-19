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


class PixelerFactory(DjangoModelFactory):

    date_joined = Faker('date_time_this_decade')
    email = Faker('email')
    first_name = Faker('first_name')
    is_active = Faker('pybool')
    is_staff = Faker('pybool')
    is_superuser = Faker('pybool')
    last_login = Faker('date_time_this_decade')
    last_name = Faker("last_name")
    password = Faker("password")
    username = Faker("user_name")

    class Meta:
        model = 'core.Pixeler'
        django_get_or_create = ('username',)


class OmicsAreaFactory(DjangoModelFactory):
    description = Faker('text', max_nb_chars=300)
    level = Faker('pyint')
    lft = Faker('pyint')
    name = Faker('word')
    rght = Faker('pyint')
    tree_id = Faker('pyint')

    class Meta:
        model = 'core.OmicsArea'
        django_get_or_create = ('name',)


class ExperimentFactory(DjangoModelFactory):
    omics_area = SubFactory(OmicsAreaFactory)
    created_at = Faker('datetime')
    description = Faker('text', max_nb_chars=300)
    released_at = Faker('datetime')
    saved_at = Faker('datetime')

    class Meta:
        model = 'core.Experiment'
        django_get_or_create = ('omics_area', 'created_at')


class AnalysisFactory(DjangoModelFactory):
    pixeler = SubFactory(PixelerFactory)
    created_at = Faker('date')
    description = Faker('text', max_nb_chars=300)
    notebook = Faker('file_path', depth=1, category=None, extension=None)
    saved_at = Faker('date')
    secondary_data = Faker('file_path', depth=1, category=None, extension=None)

    class Meta:
        model = 'core.Analysis'
        django_get_or_create = ('secondary_data', 'pixeler',)


class PixelFactory(DjangoModelFactory):

    value = Faker('pyfloat')
    quality_score = Faker('pyfloat', left_digits=0)
    omics_unit = SubFactory(OmicsUnitFactory)
    analysis = SubFactory(AnalysisFactory)

    class Meta:
        model = 'core.Pixel'
        django_get_or_create = ('value', 'omics_unit', 'analysis')
