import logging

from pathlib import Path
from shutil import copyfile
from tempfile import mkdtemp
from zipfile import ZipFile, is_zipfile

from django.utils.translation import ugettext as _

from apps.core.models import Analysis, Experiment
from apps.data.models import Entry
from apps.submission.io.xlsx import parse_template
from .. import exceptions, signals
from ..utils import make_absolute_path
from .pixel import PixelSetParser

logger = logging.getLogger(__name__)
META_FILENAME = 'meta.xlsx'


class PixelArchive(object):

    def __init__(self, archive_path):
        logger.debug('New archive: {}'.format(archive_path))

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

        self._extract()
        self._set_meta()
        self.parse()

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
                return

        raise exceptions.MetaFileRequiredError(
            _("The required meta.xlsx file is missing in your archive")
        )

    def parse(self, serialized=False):
        logger.debug('Parsing meta for {}…'.format(self.archive_path))

        self.meta = parse_template(self.meta_path, serialized=serialized)

    def save(self, pixeler):
        logger.debug('Saving data for {}…'.format(self.archive_path))

        # -- Experiment
        experiment, _ = Experiment.objects.get_or_create(
            description=self.meta['experiment']['summary'],
            omics_area=self.meta['experiment']['omics_area'],
            completed_at=self.meta['experiment']['completion_date'],
            released_at=self.meta['experiment']['release_date'],
        )

        # Add missing related entries
        entry, _ = Entry.objects.get_or_create(
            identifier=self.meta['experiment']['entry'],
            repository=self.meta['experiment']['repository']
        )
        qs = experiment.entries.filter(pk=entry.pk)
        if qs.count() < 1:
            experiment.entries.add(entry)

        # -- Analysis
        analysis, _ = Analysis.objects.get_or_create(
            description=self.meta['analysis']['description'],
            experiments__pk__in=[experiment.pk, ],
            pixeler=pixeler,
            completed_at=self.meta['analysis']['date'],
        )

        # Copy archive files to the media tree
        relative_dest = Path(
            Analysis.secondary_data_upload_to(
                analysis,
                self.meta['analysis']['secondary_data_path'].name
            )
        )
        dest = make_absolute_path(relative_dest)
        copyfile(self.meta['analysis']['secondary_data_path'], dest)
        analysis.secondary_data.name = relative_dest

        if len(self.meta['analysis']['notebook_path'].name):
            relative_dest = Path(
                Analysis.notebook_upload_to(
                    analysis,
                    self.meta['analysis']['notebook_path'].name
                )
            )
            dest = make_absolute_path(relative_dest)
            copyfile(self.meta['analysis']['notebook_path'], dest)
            analysis.notebook.name = relative_dest

        analysis.save()

        # Add missing related experiment
        qs = analysis.experiments.filter(pk=experiment.pk)
        if qs.count() < 1:
            analysis.experiments.add(experiment)

        # -- Pixels
        pixel_sets = []
        for dataset in self.meta['datasets']:
            pixelset_path, omics_unit_type, strain, description = dataset
            parser = PixelSetParser(
                pixelset_path,
                description=description,
                analysis=analysis,
                omics_unit_type=omics_unit_type,
                strain=strain
            )
            parser.parse()
            parser.save()
            pixel_sets.append(parser.pixelset)

        # Spread the word!
        logger.debug(
            'Sending importation_done signal for {}'.format(
                self.archive_path
            )
        )
        signals.importation_done.send(
            sender=self.__class__,
            experiment=experiment,
            analysis=analysis,
            pixel_sets=pixel_sets,
        )

        logger.debug(
            (
                'Saved archive data with: experiment:{}, analysis:{}, '
                'pixel_sets: {}'
            ).format(
                experiment,
                analysis,
                pixel_sets,
            )
        )
        return experiment, analysis, pixel_sets
