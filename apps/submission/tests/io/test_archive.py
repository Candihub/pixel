import datetime
import pytest

from pathlib import Path
from unittest.mock import MagicMock
from zipfile import ZipFile

from apps.core.factories import (
    AnalysisFactory, ExperimentFactory, PixelerFactory
)
from apps.core.models import (
    Analysis, Experiment, OmicsArea, OmicsUnitType, Pixel, Strain
)
from apps.core.tests import CoreFixturesTestCase
from apps.data.factories import EntryFactory
from apps.data.models import Repository
from apps.submission.io.archive import META_FILENAME, PixelArchive
from ... import exceptions, signals
from .test_pixel import LoadCGDMixin


class PixelArchiveTestCase(LoadCGDMixin, CoreFixturesTestCase):

    def setUp(self):

        self.valid_archive_path = Path(
            'apps/submission/fixtures/dataset-0001.zip'
        )
        self.no_meta_archive_path = Path(
            'apps/submission/fixtures/dataset-0001-no-meta.zip'
        )
        self.pixeler = PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )

    def test_init_with_no_archive_argument(self):

        with pytest.raises(TypeError):
            PixelArchive()

    def test_init_with_fake_archive_path(self):

        archive_path = 'foo/bar.zip'
        with pytest.raises(FileNotFoundError) as e:
            PixelArchive(archive_path)
        self.assertIn(
            "PixelArchive {} not found".format(archive_path),
            str(e)
        )

    def test_init_with_invalid_format_archive(self):

        archive_path = Path('apps/submission/fixtures/fake.zip')
        with pytest.raises(exceptions.InvalidArchiveFormatError) as e:
            PixelArchive(archive_path)
        self.assertIn(
            "Pixel submission must be a zip archive",
            str(e)
        )

    def test_init_with_valid_archive(self):

        archive = PixelArchive(self.valid_archive_path)

        self.assertEqual(archive.archive_path, self.valid_archive_path)
        self.assertIsNotNone(archive.cwd)
        z = ZipFile(self.valid_archive_path)
        expected_files = [
            archive.cwd / f for f in z.namelist()
        ]
        self.assertEqual(
            set(archive.files),
            set(expected_files)
        )
        for f in archive.files:
            self.assertTrue(f.exists())

    def test_extract(self):

        archive = PixelArchive(self.valid_archive_path)

        archive._extract()
        self.assertIsNotNone(archive.cwd)

        z = ZipFile(self.valid_archive_path)
        expected_files = [
            archive.cwd / f for f in z.namelist()
        ]
        self.assertEqual(
            set(archive.files),
            set(expected_files)
        )
        for f in archive.files:
            self.assertTrue(f.exists())

    def test_extract_cache(self):
        """Calling _extract once again should not change the cwd"""
        archive = PixelArchive(self.valid_archive_path)
        archive._extract()

        old_cwd = archive.cwd
        archive._extract()
        self.assertEqual(archive.cwd, old_cwd)

    def test_extract_force_mode(self):
        """Calling _extract in force mode should change the cwd"""
        archive = PixelArchive(self.valid_archive_path)
        archive._extract()

        old_cwd = archive.cwd
        archive._extract(force=True)
        self.assertNotEqual(archive.cwd, old_cwd)

    def test_set_meta(self):

        archive = PixelArchive(self.valid_archive_path)
        self.assertEqual(
            archive.meta_path.name,
            META_FILENAME
        )
        archive.files = [
            archive.cwd / Path('foo'),
            archive.cwd / Path('bar'),
        ]
        with pytest.raises(exceptions.MetaFileRequiredError):
            archive._set_meta()

    def test_parse(self):

        archive = PixelArchive(self.valid_archive_path)
        archive.parse()

        protein = OmicsUnitType.objects.get(name='protein')
        deltaHTU = Strain.objects.get(name='deltaHTU')
        expected = {
            'experiment': {
                'omics_area': OmicsArea.objects.get(name='Label free'),
                'completion_date': datetime.date(year=2015, month=1, day=1),
                'summary': (
                    'In these experiments, mass spectrometry analyses were '
                    'performed in yeast Candida glabrata. Proteins were '
                    'extracted using FASP protocol (by Camille Garcia from '
                    'the platform proteomics@IJM). Technical and biolocal '
                    'replicates were done in order to evaluate the '
                    'variability associated to each type of data '
                    'reproduction. Protein abundances were obtained with '
                    'PROGENESIS software, following the standard procedure '
                    'of the proteomics platform (in 2015). Note that cell '
                    'were submitted to an alkaline stress (1mL TRIS base), '
                    'to observe modifications in protein abundances.'
                ),
                'release_date': datetime.date(year=2017, month=1, day=1),
                'repository': Repository.objects.get(name='PARTNERS'),
                'entry': 'Camadro laboratory',
            },
            'analysis': {
                'secondary_data_path': archive.cwd / Path(
                    'dataset-0001/'
                    '1503002-protein-measurements-PD2.1.csv'
                ),
                'notebook_path': archive.cwd / Path('dataset-0001/NoteBook.R'),
                'description': (
                    'Protein abundances obtained in two cell growth '
                    'conditions (alkaline pH or standard) were compared, in '
                    'order to identify differentially expressed proteins. '
                    'LIMMA method was applied with default parameters, in '
                    'order to calculate p-values.'
                ),
                'date': datetime.date(year=2017, month=1, day=1),
            },
            'datasets': [
                [
                    archive.cwd / Path('dataset-0001/Pixel_C10.txt'),
                    protein,
                    deltaHTU,
                    (
                        'This set of Pixel correspond to a time point T10 '
                        '(10 minutes) after TRIS base addition in the cell '
                        'growth media.'
                    )
                ],
                [
                    archive.cwd / Path('dataset-0001/Pixel_C60.txt'),
                    protein,
                    deltaHTU,
                    (
                        'This set of Pixel correspond to a time point T10 '
                        '(10 minutes) after TRIS base addition in the cell '
                        'growth media.'
                    )
                ]
            ]
        }
        self.assertDictEqual(archive.meta, expected)

    def test_save(self):

        archive = PixelArchive(self.valid_archive_path)
        archive.parse()

        self.assertEqual(Pixel.objects.count(), 0)
        self._load_cgd_entries()
        archive.save(pixeler=self.pixeler)
        self.assertEqual(Pixel.objects.count(), 3716)
        self.assertEqual(Experiment.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)

    def test_save_emits_importation_done_signal(self):

        handler = MagicMock()
        signals.importation_done.connect(handler, sender=PixelArchive)

        archive = PixelArchive(self.valid_archive_path)
        self._load_cgd_entries()
        experiment, analysis, pixel_sets = archive.save(pixeler=self.pixeler)

        handler.assert_called_once_with(
            signal=signals.importation_done,
            sender=PixelArchive,
            experiment=experiment,
            analysis=analysis,
            pixel_sets=pixel_sets
        )

    def test_save_with_existing_experiment_and_analysis(self):

        archive = PixelArchive(self.valid_archive_path)
        archive.parse()
        self._load_cgd_entries()

        # Create experiment & analysis
        experiment = ExperimentFactory(
            description=archive.meta['experiment']['summary'],
            omics_area=archive.meta['experiment']['omics_area'],
            completed_at=archive.meta['experiment']['completion_date'],
            released_at=archive.meta['experiment']['release_date'],
        )
        entry = EntryFactory(
            identifier=archive.meta['experiment']['entry'],
            repository=archive.meta['experiment']['repository']
        )
        experiment.entries.add(entry)
        analysis = AnalysisFactory(
            description=archive.meta['analysis']['description'],
            secondary_data__from_path=archive.meta['analysis']['secondary_data_path'],  # noqa
            notebook__from_path=archive.meta['analysis']['notebook_path'],
            pixeler=self.pixeler,
            completed_at=archive.meta['analysis']['date'],
        )
        analysis.experiments.add(experiment)

        self.assertEqual(Experiment.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)

        # Import pixels
        archive.save(pixeler=self.pixeler)
        self.assertEqual(Pixel.objects.count(), 3716)

        # No new experiment/analysis should have been created
        self.assertEqual(Experiment.objects.count(), 1)
        self.assertEqual(Analysis.objects.count(), 1)
