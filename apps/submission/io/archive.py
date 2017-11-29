from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile, is_zipfile

from django.utils.translation import ugettext as _

from apps.submission.io.xlsx import parse_template
from .. import exceptions

META_FILENAME = 'meta.xlsx'


class PixelArchive(object):

    def __init__(self, archive_path):

        if not Path(archive_path).exists():
            raise FileNotFoundError(
                _("PixelArchive {} not found".format(archive_path))
            )

        if not is_zipfile(archive_path):
            raise exceptions.InvalidArchiveFormatError(
                _("Pixel submission must be a zip archive")
            )

        self.archive_path = archive_path
        self.cwd = None
        self.meta = None
        self.meta_path = None
        self.files = []

    def _extract(self, force=False):

        if self.cwd is not None and not force:
            return
        self.cwd = Path(mkdtemp())

        z = ZipFile(self.archive_path)
        z.extractall(path=self.cwd)

        self.files = [f for f in self.cwd.glob('**/*')]

    def _set_meta(self):

        for f in self.files:
            if f.name == META_FILENAME:
                self.meta_path = f
                break

    def validate(self):

        self._extract()
        self._set_meta()

        if self.meta_path is None:
            raise exceptions.MetaFileRequiredError(
                _("The required meta.xlsx file is missing in your archive")
            )

    def parse_meta(self, serialized=False):

        self.validate()
        self.meta = parse_template(self.meta_path, serialized=serialized)
