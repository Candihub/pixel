from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from ...io.parsers import CGDParser, SGDParser


class Command(BaseCommand):
    SUPPORTED_DATABASES = (
        'CGD',
        'SGD',
    )
    help = _("Load entries from various repositories")

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            help=_("Path to the file containing chromosome features (.tab)")
        )
        parser.add_argument(
            '--database',
            choices=self.SUPPORTED_DATABASES,
            required=True,
            help=_("The database related to the file (REQUIRED)")
        )
        parser.add_argument(
            '--ignore-aliases',
            action='store_true',
            help=_("Ignore aliases in omics units/entries")
        )

    def handle(self, *args, **options):
        filename = options.get('filename')
        database = options.get('database')
        ignore_aliases = options.get('ignore_aliases', False)

        if database == 'CGD':
            chrParser = CGDParser(Path(filename))
        elif database == 'SGD':
            chrParser = SGDParser(Path(filename))

        chrParser.parse()
        chrParser.save(ignore_aliases=ignore_aliases)

        self.stdout.write(
            self.style.SUCCESS(
                _("Successfully imported file: {}".format(filename))
            )
        )
