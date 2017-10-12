import datetime

from django.db import IntegrityError, transaction
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


class StrainTestCase(TestCase):

    def setUp(self):

        self.species_name = 'Saccharomyces cerevisiae'
        self.species_reference = EntryFactory()
        self.species_description = 'lorem ipsum'
        self.species = models.Species.objects.create(
            name=self.species_name,
            reference=self.species_reference,
            description=self.species_description
        )

    def test_can_create_strain(self):

        name = 'S288c / XJ24-24a'
        description = 'lorem ipsum'

        qs = models.Strain.objects.all()
        self.assertEqual(qs.count(), 0)

        strain = models.Strain.objects.create(
            name=name,
            description=description,
            species=self.species
        )

        self.assertEqual(strain.name, name)
        self.assertEqual(strain.description, description)
        self.assertEqual(strain.species.id, self.species.id)
        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):

        name = 'S288c / XJ24-24a'

        strain = models.Strain.objects.create(
            name=name,
            species=self.species
        )

        self.assertEqual(str(strain), name)

    def test_cannot_create_two_strains_with_identical_names_for_species(self):

        name = 'S288c / XJ24-24a'

        qs = models.Strain.objects.all()
        self.assertEqual(qs.count(), 0)

        models.Strain.objects.create(
            name=name,
            species=self.species
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                models.Strain.objects.create(
                    name=name,
                    species=self.species
                )

        self.assertEqual(qs.count(), 1)


class OmicsUnitTypeTestCase(TestCase):

    def test_can_create_omics_unit_type(self):
        # TODO
        # raise NotImplementedError('You have work to do @thomasdenecker!')
        pass

    def test_model_representation(self):
        # TODO
        # raise NotImplementedError('You have work to do @thomasdenecker!')
        pass


class OmicsUnitTestCase(TestCase):

    def setUp(self):

        species = models.Species.objects.create(
            name='Saccharomyces cerevisiae',
            reference=EntryFactory(),
            description='lorem ipsum',
        )
        self.strain = models.Strain.objects.create(
            name='S288c / XJ24-24a',
            species=species,
        )
        self.reference = EntryFactory()
        self.type = models.OmicsUnitType.objects.create(
            name='Promoter',
        )

    def test_can_create_omics_unit(self):

        qs = models.OmicsUnit.objects.all()
        self.assertEqual(qs.count(), 0)

        omics_unit = models.OmicsUnit.objects.create(
            reference=self.reference,
            strain=self.strain,
            type=self.type
        )

        self.assertEqual(omics_unit.reference.id, self.reference.id)
        self.assertEqual(omics_unit.strain.id, self.strain.id)
        self.assertEqual(omics_unit.type.id, self.type.id)

        self.assertEqual(qs.count(), 1)

    def test_omics_unit_default_status(self):

        omics_unit = models.OmicsUnit.objects.create(
            reference=self.reference,
            strain=self.strain,
            type=self.type
        )

        self.assertEqual(omics_unit.status, models.OmicsUnit.STATUS_DUBIOUS)

    def test_create_omics_unit_with_non_default_status(self):

        omics_unit = models.OmicsUnit.objects.create(
            reference=self.reference,
            strain=self.strain,
            type=self.type,
            status=models.OmicsUnit.STATUS_INVALID
        )

        self.assertEqual(omics_unit.status, models.OmicsUnit.STATUS_INVALID)

    def test_model_representation(self):
        # TODO
        # raise NotImplementedError('You have work to do @thomasdenecker!')
        pass

    def test_cannot_create_two_omics_units_with_same_reference_type_and_strain_(self):  # noqa
        # TODO
        # raise NotImplementedError('You have work to do @thomasdenecker!')
        pass


class PixelTestCase(TestCase):

    def setUp(self):

        # OmicsUnit
        species = models.Species.objects.create(
            name='Saccharomyces cerevisiae',
            reference=EntryFactory(),
            description='lorem ipsum',
        )
        strain = models.Strain.objects.create(
            name='S288c / XJ24-24a',
            species=species,
        )
        reference = EntryFactory()
        type = models.OmicsUnitType.objects.create(name='Promoter')
        self.omics_unit = models.OmicsUnit.objects.create(
            reference=reference,
            strain=strain,
            type=type,
        )

        # Analysis
        omics_area = models.OmicsArea.objects.create(name='RNAseq')
        experiment = models.Experiment.objects.create(
            omics_area=omics_area,
            released_at=datetime.date(1980, 10, 14),
        )
        pixeler = models.Pixeler.objects.create(
            username='johndoe',
            email='john@doe.com',
            password='toto,1234!'
        )
        self.analysis = models.Analysis.objects.create(
            secondary_data='/fake/path/secondary_data',
            pixeler=pixeler,
        )
        self.analysis.experiments.add(experiment)

    def test_can_create_pixel(self):

        qs = models.Pixel.objects.all()
        self.assertEqual(qs.count(), 0)

        value = 42.42
        quality_score = 0.54
        pixel = models.Pixel.objects.create(
            value=value,
            quality_score=quality_score,
            omics_unit=self.omics_unit,
            analysis=self.analysis,
        )

        self.assertEqual(pixel.value, value)
        self.assertEqual(pixel.quality_score, quality_score)
        self.assertEqual(pixel.omics_unit.id, self.omics_unit.id)
        self.assertEqual(pixel.analysis.id, self.analysis.id)

        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):

        pixel = models.Pixel.objects.create(
            value=42.42,
            quality_score=0.54,
            omics_unit=self.omics_unit,
            analysis=self.analysis,
        )

        self.assertEqual(str(pixel), str(pixel.id))


class ExperimentTestCase(TestCase):

    def setUp(self):

        self.omics_area = models.OmicsArea.objects.create(name='RNAseq')

    def test_can_create_experiment_without_entries_or_tags(self):

        qs = models.Experiment.objects.all()
        self.assertEqual(qs.count(), 0)

        description = 'lorem ipsum'
        released_at = datetime.date(1980, 10, 14)
        experiment = models.Experiment.objects.create(
            description=description,
            omics_area=self.omics_area,
            released_at=released_at,
        )

        self.assertEqual(experiment.description, description)
        self.assertEqual(experiment.released_at, released_at)
        self.assertEqual(experiment.omics_area.id, self.omics_area.id)
        self.assertEqual(experiment.entries.count(), 0)
        self.assertEqual(experiment.tags.count(), 0)

        self.assertEqual(qs.count(), 1)

    def test_can_add_entries_to_experiment(self):

        experiment = models.Experiment.objects.create(
            description='lorem ipsum',
            omics_area=self.omics_area,
            released_at=datetime.date(1980, 10, 14),
        )
        entries = [EntryFactory() for e in range(2)]
        experiment.entries.add(*entries)

        self.assertEqual(experiment.entries.count(), len(entries))

    def test_can_add_tags_to_experiment(self):

        experiment = models.Experiment.objects.create(
            description='lorem ipsum',
            omics_area=self.omics_area,
            released_at=datetime.date(1980, 10, 14),
        )

        tags = ['ph', 'NaOH 3M']
        experiment.tags = tags
        experiment.save()

        self.assertEqual(models.Tag.objects.count(), len(experiment.tags))
        self.assertEqual(models.Tag.objects.count(), len(tags))


class AnalysisTestCase(TestCase):

    def setUp(self):

        omics_area = models.OmicsArea.objects.create(name='RNAseq')
        self.experiment = models.Experiment.objects.create(
            omics_area=omics_area,
            released_at=datetime.date(1980, 10, 14),
        )
        self.pixeler = models.Pixeler.objects.create(
            username='johndoe',
            email='john@doe.com',
            password='toto,1234!'
        )

    def test_can_create_analysis_without_experiments_or_tags(self):

        qs = models.Analysis.objects.all()
        self.assertEqual(qs.count(), 0)

        description = 'lorem ipsum'
        secondary_data = '/fake/path/secondary_data'
        notebook = '/fake/path/notebook'
        analysis = models.Analysis.objects.create(
            description=description,
            secondary_data=secondary_data,
            notebook=notebook,
            pixeler=self.pixeler,
        )

        self.assertEqual(analysis.description, description)
        self.assertEqual(analysis.secondary_data, secondary_data)
        self.assertEqual(analysis.notebook, notebook)
        self.assertEqual(analysis.pixeler.id, self.pixeler.id)
        self.assertEqual(analysis.experiments.count(), 0)
        self.assertEqual(analysis.tags.count(), 0)

        self.assertEqual(qs.count(), 1)

    def test_can_create_analysis_with_experiments(self):

        analysis = models.Analysis.objects.create(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            notebook='/fake/path/notebook',
            pixeler=self.pixeler,
        )
        analysis.experiments.add(self.experiment)

        self.assertEqual(analysis.experiments.count(), 1)
        self.assertEqual(analysis.tags.count(), 0)

    def test_can_create_analysis_with_tags(self):

        analysis = models.Analysis.objects.create(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            notebook='/fake/path/notebook',
            pixeler=self.pixeler,
        )
        tags = ['foo technique', 'bar technique']
        analysis.tags = tags
        analysis.save()

        self.assertEqual(analysis.tags.count(), len(analysis.tags))
        self.assertEqual(analysis.tags.count(), len(tags))

    def test_secondary_data_upload_to(self):

        analysis = models.Analysis(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            pixeler=self.pixeler,
        )

        upload_path = models.Analysis.secondary_data_upload_to(
            analysis,
            'misc.csv'
        )
        expected = '{}/{}/secondary_data'.format(
            analysis.pixeler.id, analysis.id
        )

        self.assertEqual(upload_path, expected)

    def test_notebook_upload_to(self):

        analysis = models.Analysis(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            pixeler=self.pixeler,
        )

        upload_path = models.Analysis.notebook_upload_to(
            analysis,
            'misc.csv'
        )
        expected = '{}/{}/notebook'.format(
            analysis.pixeler.id, analysis.id
        )

        self.assertEqual(upload_path, expected)
