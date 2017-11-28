import pytest

from pathlib import Path
from zipfile import ZipFile

from django.test import TestCase

from apps.submission.io.archive import META_FILENAME, PixelArchive
from ... import exceptions


class PixelArchiveTestCase(TestCase):

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
        self.assertEqual(archive.cwd, None)
        self.assertListEqual(archive.files, [])

    def test_extract(self):

        archive = PixelArchive(self.valid_archive_path)

        archive._extract()
        self.assertIsNotNone(archive.cwd)

        expected_files = [
            archive.cwd / f for f in ZipFile(self.valid_archive_path).namelist()
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

        archive._set_meta()
        self.assertIsNone(archive.meta)

        archive._extract()
        archive._set_meta()
        self.assertEqual(
            archive.meta.name,
            META_FILENAME
        )

    def test_validate(self):

        archive = PixelArchive(self.no_meta_archive_path)

        with pytest.raises(exceptions.MetaFileRequiredError) as e:
            archive.validate()
        self.assertIn(
            "The required meta.xlsx file is missing in your archive",
            str(e)
        )
