import datetime

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.data.factories import EntryFactory, RepositoryFactory
from .. import models, factories
from . import CoreFixturesTestCase


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

    def test_can_create_species_with_repository(self):

        name = 'Saccharomyces cerevisiae'
        repository = RepositoryFactory()
        description = 'lorem ipsum'

        qs = models.Species.objects.all()
        self.assertEqual(qs.count(), 0)

        species = models.Species.objects.create(
            name=name,
            repository=repository,
            description=description,
        )

        self.assertEqual(species.name, name)
        self.assertEqual(species.repository.id, repository.id)
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

    def test_can_create_species_without_reference_or_repository(self):

        name = 'Saccharomyces cerevisiae'

        qs = models.Species.objects.all()
        self.assertEqual(qs.count(), 0)

        species = models.Species.objects.create(
            name=name,
        )

        self.assertEqual(species.name, name)
        self.assertEqual(species.reference, None)
        self.assertEqual(species.repository, None)
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
        reference = EntryFactory()

        qs = models.Strain.objects.all()
        self.assertEqual(qs.count(), 0)

        strain = models.Strain.objects.create(
            name=name,
            description=description,
            species=self.species,
            reference=reference,
        )

        self.assertEqual(strain.name, name)
        self.assertEqual(strain.description, description)
        self.assertEqual(strain.species.id, self.species.id)
        self.assertEqual(strain.reference.id, reference.id)
        self.assertEqual(qs.count(), 1)

    def test_can_create_strain_without_reference(self):

        name = 'S288c / XJ24-24a'

        qs = models.Strain.objects.all()
        self.assertEqual(qs.count(), 0)

        strain = models.Strain.objects.create(
            name=name,
            species=self.species,
        )

        self.assertEqual(strain.name, name)
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
        name = 'gene'
        description = 'lorem ipsum'

        qs = models.OmicsUnitType.objects.all()
        self.assertEqual(qs.count(), 0)

        omics_unit_type = models.OmicsUnitType.objects.create(
            name=name,
            description=description
        )

        self.assertEqual(omics_unit_type.name, name)
        self.assertEqual(omics_unit_type.description, description)
        self.assertEqual(qs.count(), 1)

    def test_model_representation(self):
        name = 'gene'

        omics_unit_type = models.OmicsUnitType.objects.create(
            name=name
        )

        self.assertEqual(str(omics_unit_type), name)


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

        omics_unit = models.OmicsUnit.objects.create(
            reference=self.reference,
            strain=self.strain,
            type=self.type,
        )

        custom_id = '{} ({}/{}/{})'.format(
            omics_unit.id.hex[:7],
            omics_unit.type,
            omics_unit.strain,
            omics_unit.strain.species.name
        )

        self.assertEqual(str(omics_unit), str(custom_id))

    def test_cannot_create_two_omics_units_with_same_reference_type_and_strain_(self):  # noqa

        qs = models.OmicsUnit.objects.all()
        self.assertEqual(qs.count(), 0)

        models.OmicsUnit.objects.create(
            reference=self.reference,
            strain=self.strain,
            type=self.type
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                models.OmicsUnit.objects.create(
                    reference=self.reference,
                    strain=self.strain,
                    type=self.type
                )

        self.assertEqual(qs.count(), 1)


class PixelSetTestCase(CoreFixturesTestCase):

    def setUp(self):

        self.experiment = factories.ExperimentFactory()
        self.pixel_set = factories.PixelSetFactory()
        self.n_pixels = 10
        self.pixel_set.analysis.experiments.add(self.experiment)
        factories.PixelFactory.create_batch(
            self.n_pixels,
            pixel_set=self.pixel_set
        )

    def test_can_create_pixel_set(self):

        analysis = factories.AnalysisFactory(
            secondary_data__from_path=factories.SECONDARY_DATA_DEFAULT_PATH,
            notebook__from_path=factories.NOTEBOOK_DEFAULT_PATH,
        )
        pixels_file_path = '/foo/bar/lol'
        pixel_set = factories.PixelSetFactory(
            analysis=analysis,
            pixels_file=pixels_file_path
        )

        self.assertEqual(pixel_set.analysis.id, analysis.id)
        self.assertEqual(pixel_set.pixels_file, pixels_file_path)

    def test_pixelset_upload_to(self):

        pixeler = factories.PixelerFactory()
        analysis = factories.AnalysisFactory(
            secondary_data__from_path=factories.SECONDARY_DATA_DEFAULT_PATH,
            notebook__from_path=factories.NOTEBOOK_DEFAULT_PATH,
            pixeler=pixeler
        )
        pixel_set = factories.PixelSetFactory(
            analysis=analysis,
            pixels_file__from_path=factories.PIXELS_DEFAULT_PATH,
        )

        pixel_filename = 'misc.csv'
        upload_path = models.PixelSet.pixelset_upload_to(
            pixel_set,
            pixel_filename
        )
        expected = '{}/analyses/{}/pixelsets/{}'.format(
            pixel_set.analysis.pixeler.id,
            pixel_set.analysis.id,
            pixel_filename
        )

        self.assertEqual(upload_path, expected)

    def test_get_omics_areas(self):

        expected = [self.experiment.omics_area.name, ]
        self.assertEqual(
            list(self.pixel_set.get_omics_areas()),
            expected
        )

        # Test distinct
        new_experiment = factories.ExperimentFactory(
            omics_area=self.experiment.omics_area
        )
        self.pixel_set.analysis.experiments.add(new_experiment)
        self.assertEqual(
            list(self.pixel_set.get_omics_areas()),
            expected
        )

    def test_get_omics_unit_types(self):

        types = list(self.pixel_set.get_omics_unit_types())
        types.sort()
        expected = list(
            models.OmicsUnitType.objects.values_list('name', flat=True)
        )
        expected.sort()
        self.assertEqual(types, expected)

    def test_get_species(self):

        expected = models.Species.objects.values_list('name', flat=True)
        self.assertEqual(
            list(self.pixel_set.get_species()),
            list(expected),
        )


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
            completed_at=datetime.date(1980, 10, 14),
            released_at=datetime.date(1980, 10, 14),
        )
        pixeler = models.Pixeler.objects.create(
            username='johndoe',
            email='john@doe.com',
            password='toto,1234!'
        )
        self.analysis = models.Analysis.objects.create(
            pixeler=pixeler,
            completed_at=datetime.date(1980, 10, 14),
        )
        self.analysis.secondary_data.name = (
            factories.SECONDARY_DATA_DEFAULT_PATH
        )
        self.analysis.save()
        self.analysis.experiments.add(experiment)

        # Pixel set
        self.pixel_set = factories.PixelSetFactory(
            analysis=self.analysis,
            pixels_file__from_path=factories.PIXELS_DEFAULT_PATH,
        )

    def test_can_create_pixel(self):

        qs = models.Pixel.objects.all()
        self.assertEqual(qs.count(), 0)

        value = 42.42
        quality_score = 0.54
        pixel = models.Pixel.objects.create(
            value=value,
            quality_score=quality_score,
            omics_unit=self.omics_unit,
            pixel_set=self.pixel_set,
        )

        self.assertEqual(pixel.value, value)
        self.assertEqual(pixel.quality_score, quality_score)
        self.assertEqual(pixel.omics_unit.id, self.omics_unit.id)
        self.assertEqual(pixel.pixel_set.id, self.pixel_set.id)

        self.assertEqual(qs.count(), 1)


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
            completed_at=datetime.date(1980, 10, 14),
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
            completed_at=datetime.date(1980, 10, 14),
            released_at=datetime.date(1980, 10, 14),
        )
        entries = [EntryFactory() for e in range(2)]
        experiment.entries.add(*entries)

        self.assertEqual(experiment.entries.count(), len(entries))

    def test_can_add_tags_to_experiment(self):

        experiment = models.Experiment.objects.create(
            description='lorem ipsum',
            omics_area=self.omics_area,
            completed_at=datetime.date(1980, 10, 14),
            released_at=datetime.date(1980, 10, 14),
        )

        tags = ['ph', 'NaOH 3M']
        experiment.tags = ', '.join(tags)
        experiment.save()

        self.assertEqual(models.Tag.objects.count(), len(experiment.tags))
        self.assertEqual(models.Tag.objects.count(), len(tags))

    def test_can_add_hierarchical_tags_to_experiment(self):

        experiment = models.Experiment.objects.create(
            description='lorem ipsum',
            omics_area=self.omics_area,
            completed_at=datetime.date(1980, 10, 14),
            released_at=datetime.date(1980, 10, 14),
        )

        tags = ['condition/ph/high', 'condition/salt/NaOH 3M']
        experiment.tags = ', '.join(tags)
        experiment.save()

        expected_tags = list(
            set([t.strip() for tag in tags for t in tag.split('/')])
        )
        expected_experiment_tags = [tag.split('/')[-1] for tag in tags]

        self.assertEqual(
            models.Tag.objects.count(),
            len(expected_tags)
        )
        self.assertEqual(
            experiment.tags.count(),
            len(expected_experiment_tags)
        )


class AnalysisTestCase(TestCase):

    def setUp(self):

        omics_area = models.OmicsArea.objects.create(name='RNAseq')
        self.experiment = models.Experiment.objects.create(
            omics_area=omics_area,
            completed_at=datetime.date(1980, 10, 14),
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
            completed_at=datetime.date(1980, 10, 14),
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
            completed_at=datetime.date(1980, 10, 14),
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
            completed_at=datetime.date(1980, 10, 14),
        )
        tags = ['foo technique', 'bar technique']
        analysis.tags = tags
        analysis.save()

        self.assertEqual(analysis.tags.count(), len(analysis.tags))
        self.assertEqual(analysis.tags.count(), len(tags))

    def test_can_add_hierarchical_tags_to_analysis(self):

        analysis = models.Analysis.objects.create(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            notebook='/fake/path/notebook',
            pixeler=self.pixeler,
            completed_at=datetime.date(1980, 10, 14),
        )

        tags = ['foo/bar/pca', 'foo/bayes']
        analysis.tags = ', '.join(tags)
        analysis.save()

        expected_tags = list(
            set([t.strip() for tag in tags for t in tag.split('/')])
        )
        expected_experiment_tags = [tag.split('/')[-1] for tag in tags]

        self.assertEqual(
            models.Tag.objects.count(),
            len(expected_tags)
        )
        self.assertEqual(
            analysis.tags.count(),
            len(expected_experiment_tags)
        )

    def test_secondary_data_upload_to(self):

        analysis = models.Analysis(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            pixeler=self.pixeler,
            completed_at=datetime.date(1980, 10, 14),
        )

        secondary_data_filename = 'misc.csv'
        upload_path = models.Analysis.secondary_data_upload_to(
            analysis,
            secondary_data_filename
        )
        expected = '{}/analyses/{}/secondary_data/{}'.format(
            analysis.pixeler.id,
            analysis.id,
            secondary_data_filename
        )

        self.assertEqual(upload_path, expected)

    def test_notebook_upload_to(self):

        analysis = models.Analysis(
            description='lorem ipsum',
            secondary_data='/fake/path/secondary_data',
            pixeler=self.pixeler,
            completed_at=datetime.date(1980, 10, 14),
        )

        notebook_filename = 'misc.csv'
        upload_path = models.Analysis.notebook_upload_to(
            analysis,
            notebook_filename
        )
        expected = '{}/analyses/{}/notebook/{}'.format(
            analysis.pixeler.id,
            analysis.id,
            notebook_filename
        )

        self.assertEqual(upload_path, expected)


class OmicsAreaTestCase(TestCase):

    def test_can_create_omics_area(self):

        qs = models.OmicsArea.objects.all()
        self.assertEqual(qs.count(), 0)

        name = 'RNAseq'
        description = 'lorem ipsum'

        omics_area = models.OmicsArea.objects.create(
            name=name,
            description=description,
        )

        self.assertEqual(omics_area.name, name)
        self.assertEqual(omics_area.description, description)
        self.assertEqual(qs.count(), 1)

    def test_can_create_omics_area_tree(self):

        qs = models.OmicsArea.objects.all()
        self.assertEqual(qs.count(), 0)

        root_omics_area = models.OmicsArea.objects.create(
            name='Genomics',
        )
        child_omics_area = models.OmicsArea.objects.create(
            name='RNAseq',
            parent=root_omics_area,
        )

        self.assertEqual(
            root_omics_area.children.get().name,
            child_omics_area.name,
        )
        self.assertEqual(
            child_omics_area.parent.name,
            root_omics_area.name,
        )
        self.assertEqual(qs.count(), 2)

    def test_omics_area_tree_order_insertion_by_name(self):

        qs = models.OmicsArea.objects.all()
        self.assertEqual(qs.count(), 0)

        root_omics_area = models.OmicsArea.objects.create(
            name='Genomics',
        )
        first_child_omics_area = models.OmicsArea.objects.create(
            name='RNAseq',
            parent=root_omics_area,
        )
        second_child_omics_area = models.OmicsArea.objects.create(
            name='Microarrays',
            parent=root_omics_area,
        )
        third_child_omics_area = models.OmicsArea.objects.create(
            name='SAGE',
            parent=root_omics_area,
        )

        self.assertEqual(
            root_omics_area.children.all()[0].name,
            second_child_omics_area.name,
        )
        self.assertEqual(
            root_omics_area.children.all()[1].name,
            first_child_omics_area.name,
        )
        self.assertEqual(
            root_omics_area.children.all()[2].name,
            third_child_omics_area.name,
        )
        self.assertEqual(qs.count(), 4)

    def test_model_representation(self):

        name = 'RNAseq'
        description = 'lorem ipsum'

        omics_area = models.OmicsArea.objects.create(
            name=name,
            description=description,
        )

        self.assertEqual(str(omics_area), name)


class PixelerTestCase(TestCase):

    def test_can_create_pixeler(self):

        qs = models.Pixeler.objects.all()
        self.assertEqual(qs.count(), 0)

        username = 'johndoe'
        email = 'john@doe.com'
        pixeler = models.Pixeler.objects.create(
            username=username,
            email=email,
            password='toto,1234!'
        )

        self.assertEqual(pixeler.username, username)
        self.assertEqual(pixeler.email, email)
        self.assertEqual(qs.count(), 1)
