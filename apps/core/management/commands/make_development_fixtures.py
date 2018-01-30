import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from apps.core import factories

DEFAULT_N_EXPERIMENTS = 3
DEFAULT_N_PIXELS_PER_SET = 20
DEFAULT_N_PIXELSETS = 10

logger = logging.getLogger(__name__)


def make_development_fixtures(n_pixel_sets=DEFAULT_N_PIXELSETS,
                              n_experiments=DEFAULT_N_EXPERIMENTS,
                              n_pixels_per_set=DEFAULT_N_PIXELS_PER_SET):
    """Generate development fixtures"""
    logger.debug(
        (
            "Will generate {} experiments and {} pixel sets with {} "
            "pixels each"
        ).format(
            n_experiments, n_pixel_sets, n_pixels_per_set
        )
    )

    # Experiment
    experiments = factories.ExperimentFactory.create_batch(n_experiments)

    # PixelSet
    pixel_sets = factories.PixelSetFactory.create_batch(n_pixel_sets)

    index = 0
    for pixel_set in pixel_sets:

        # Link analysis to experiment
        experiment = experiments[index % len(experiments)]
        pixel_set.analysis.experiments.add(experiment)

        # Create pixels
        factories.PixelFactory.create_batch(
            n_pixels_per_set,
            pixel_set=pixel_set
        )

        index = index + 1


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
        parser.add_argument(
            '--experiments',
            type=int,
            action='store',
            default=DEFAULT_N_EXPERIMENTS,
            help=_("the number of experiment(s) to generate")
        )
        parser.add_argument(
            '--pixels',
            type=int,
            action='store',
            default=DEFAULT_N_PIXELS_PER_SET,
            help=_("the number of pixel(s) per pixel set")
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
        n_experiments = options.get('experiments', DEFAULT_N_EXPERIMENTS)
        n_pixels_per_set = options.get('pixels', DEFAULT_N_PIXELS_PER_SET)

        self.stdout.write(
            _(
                "Will generate {} experiments and {} pixel sets with {} "
                "pixels each…"
            ).format(
                n_experiments, n_pixel_sets, n_pixels_per_set
            )
        )

        make_development_fixtures(
            n_pixel_sets=n_pixel_sets,
            n_experiments=n_experiments,
            n_pixels_per_set=n_pixels_per_set
        )

        self.stdout.write(
            self.style.SUCCESS(
                _("Successfully generated fixtures")
            )
        )
