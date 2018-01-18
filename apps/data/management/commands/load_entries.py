from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from ...io.parsers import CGDParser


class Command(BaseCommand):
    help = _("Load entries from various repositories")

    def add_arguments(self, parser):
        parser.add_argument(
            '--cgd',
            help=_("Load entries from CGD chromosome features (.tab)")
        )
        parser.add_argument(
            '--ignore-aliases',
            action='store_true',
            help=_("Ignore aliases in omics units/entries")
        )

    def handle(self, *args, **options):

        cgd = options.get('cgd', None)
        ignore_aliases = options.get('ignore_aliases', False)

        if cgd is None:
            raise CommandError(
                _(
                    "You need to provide at least one cgd file to import. "
                    "See usage (-h)."
                )
            )

        cgd_parser = CGDParser(Path(cgd))
        cgd_parser.parse()
        cgd_parser.save(ignore_aliases=ignore_aliases)

        self.stdout.write(
            self.style.SUCCESS(
                _("Successfully imported CGD file: {}".format(cgd))
            )
        )
