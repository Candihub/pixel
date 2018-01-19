from pathlib import Path

from django.utils.timezone import get_default_timezone
from factory import (
    Faker, Iterator, PostGenerationMethodCall,
    post_generation as fb_post_generation, SubFactory
)
from factory.django import DjangoModelFactory, FileField as fb_FileField

from apps.data.factories import EntryFactory, RepositoryFactory
from . import models

PIXELER_PASSWORD = 'SurferRosa1988'
SECONDARY_DATA_DEFAULT_PATH = Path(
    'apps/submission/fixtures/dataset-0001/'
) / Path(
    '1503002-protein-measurements-PD2.1.csv'
)
NOTEBOOK_DEFAULT_PATH = Path(
    'apps/submission/fixtures/dataset-0001/NoteBook.R'
)
PIXELS_DEFAULT_PATH = Path('apps/core/fixtures/Pixel_C10.txt')


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
    species = Iterator(models.Species.objects.all())
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
    strain = Iterator(models.Strain.objects.all())
    type = Iterator(models.OmicsUnitType.objects.all())
    status = Iterator(s[0] for s in models.OmicsUnit.STATUS_CHOICES)

    class Meta:
        model = 'core.OmicsUnit'
        django_get_or_create = ('reference', 'strain')


class PixelerFactory(DjangoModelFactory):

    username = Faker('user_name')
    password = PostGenerationMethodCall(
        'set_password', PIXELER_PASSWORD
    )
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = Faker('pybool')
    is_staff = Faker('pybool')
    is_superuser = Faker('pybool')
    date_joined = Faker('date_time_this_decade', tzinfo=get_default_timezone())
    last_login = Faker('date_time_this_decade', tzinfo=get_default_timezone())

    class Meta:
        model = 'core.Pixeler'
        django_get_or_create = ('username',)


class OmicsAreaFactory(DjangoModelFactory):

    name = Faker('word')
    description = Faker('text', max_nb_chars=300)

    class Meta:
        model = 'core.OmicsArea'
        django_get_or_create = ('name',)


class ExperimentFactory(DjangoModelFactory):

    omics_area = Iterator(models.OmicsArea.objects.all())
    description = Faker('text', max_nb_chars=300)
    completed_at = Faker('date')
    released_at = Faker('date')
    created_at = Faker('date_time', tzinfo=get_default_timezone())
    saved_at = Faker('date_time', tzinfo=get_default_timezone())

    class Meta:
        model = 'core.Experiment'
        django_get_or_create = ('omics_area', 'description')


class AnalysisFactory(DjangoModelFactory):

    description = Faker('text', max_nb_chars=300)
    pixeler = SubFactory(PixelerFactory)
    notebook = fb_FileField(
        filename=Faker('file_path', depth=0, extension='R')
    )
    secondary_data = fb_FileField(
        filename=Faker('file_path', depth=0, extension='csv')
    )
    completed_at = Faker('date')
    created_at = Faker('date_time', tzinfo=get_default_timezone())
    saved_at = Faker('date_time', tzinfo=get_default_timezone())

    class Meta:
        model = 'core.Analysis'
        django_get_or_create = ('description', 'pixeler')

    @fb_post_generation
    def experiments(self, create, experiments, **kwargs):
        if not create or not experiments:
            # Simple build, do nothing.
            return

        for experiment in experiments:
            self.experiments.add(experiment)


class PixelSetFactory(DjangoModelFactory):

    pixels_file = fb_FileField(
        filename=Faker('file_path', depth=0, extension='csv')
    )
    description = Faker('text', max_nb_chars=300)
    analysis = SubFactory(AnalysisFactory)

    class Meta:
        model = 'core.PixelSet'


class PixelFactory(DjangoModelFactory):

    value = Faker('pyfloat')
    quality_score = Faker('pyfloat', left_digits=0)
    omics_unit = SubFactory(OmicsUnitFactory)
    pixel_set = SubFactory(PixelSetFactory)

    class Meta:
        model = 'core.Pixel'
        django_get_or_create = ('value', 'omics_unit', 'pixel_set')
