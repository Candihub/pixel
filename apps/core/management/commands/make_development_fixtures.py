from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from apps.core.factories import PixelSetFactory

DEFAULT_N_PIXELSETS = 10


def make_development_fixtures(n_pixel_sets=DEFAULT_N_PIXELSETS):
    """Generate development fixtures"""

    PixelSetFactory.create_batch(n_pixel_sets)


class Command(BaseCommand):
    help = _("Generate development fixtures")

    def add_arguments(self, parser):
        parser.add_argument(
            '--pixel-sets',
            type=int,
            action='store',
            default=DEFAULT_N_PIXELSETS,
            help=_("the number of pixel set(s) to generate")
        )

    def handle(self, *args, **options):

        if not settings.DEBUG:
            raise CommandError(
                _(
                    "This command should only be used in development, "
                    "i.e. with DEBUG=True"
                )
            )

        n_pixel_sets = options.get('pixel_sets', DEFAULT_N_PIXELSETS)

        self.stdout.write(
            _("Will generate {} pixel sets…".format(n_pixel_sets))
        )

        make_development_fixtures(n_pixel_sets=n_pixel_sets)

        self.stdout.write(
            self.style.SUCCESS(
                _("Successfully generated fixtures")
            )
        )
