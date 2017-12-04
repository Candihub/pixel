import datetime
import pytest

from pathlib import Path
from zipfile import ZipFile

from django.test import TestCase

from apps.core.models import OmicsArea, OmicsUnitType, Strain
from apps.data.models import Repository
from apps.submission.io.archive import META_FILENAME, PixelArchive
from ... import exceptions


class PixelArchiveTestCase(TestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    def setUp(self):

        self.valid_archive_path = Path(
            'apps/submission/fixtures/dataset-0001.zip'
        )
        self.no_meta_archive_path = Path(
            'apps/submission/fixtures/dataset-0001-no-meta.zip'
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

    def test_parse_meta(self):

        archive = PixelArchive(self.valid_archive_path)
        archive.parse_meta()

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
