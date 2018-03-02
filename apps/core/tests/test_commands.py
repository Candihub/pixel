from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils.six import StringIO

from ..management.commands.make_development_fixtures import (
    DEFAULT_N_EXPERIMENTS,
    DEFAULT_N_PIXELS_PER_SET,
    DEFAULT_N_PIXELSETS,
)
from .. import models
from . import CoreFixturesTestCase


@override_settings(DEBUG=True)
class MakeDevelopmentFixturesCommandTestCase(CoreFixturesTestCase):

    def test_command(self):

        output = StringIO()

        with self.settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command('make_development_fixtures', stdout=output)

        self.assertEqual(models.PixelSet.objects.count(), 0)
        self.assertEqual(models.Experiment.objects.count(), 0)
        self.assertEqual(models.Pixel.objects.count(), 0)

        call_command('make_development_fixtures', stdout=output, no_color=True)

        n_pixelsets = models.PixelSet.objects.count()
        self.assertEqual(
            n_pixelsets,
            DEFAULT_N_PIXELSETS
        )
        self.assertEqual(
            models.Experiment.objects.count(),
            DEFAULT_N_EXPERIMENTS
        )
        self.assertEqual(
            models.Pixel.objects.count(),
            n_pixelsets * DEFAULT_N_PIXELS_PER_SET
        )

        pixel_set = models.PixelSet.objects.first()
        self.assertTrue(pixel_set.cached_species)
        self.assertTrue(pixel_set.cached_omics_areas)
        self.assertTrue(pixel_set.cached_omics_unit_types)

        expected_output = (
            'Will generate {} experiments and {} pixel sets with {} '
            'pixels each…\n'
            'Successfully generated fixtures'
        ).format(
            DEFAULT_N_EXPERIMENTS,
            DEFAULT_N_PIXELSETS,
            DEFAULT_N_PIXELS_PER_SET
        )
        self.assertIn(expected_output, output.getvalue())

    def test_command_with_custom_options(self):

        output = StringIO()

        n_pixel_sets = 5
        n_experiments = 2
        n_pixels_per_set = 2

        self.assertEqual(models.PixelSet.objects.count(), 0)
        self.assertEqual(models.Experiment.objects.count(), 0)
        self.assertEqual(models.Pixel.objects.count(), 0)

        call_command(
            'make_development_fixtures',
            pixel_sets=n_pixel_sets,
            experiments=n_experiments,
            pixels=n_pixels_per_set,
            stdout=output,
            no_color=True
        )

        self.assertEqual(
            models.PixelSet.objects.count(),
            n_pixel_sets
        )
        self.assertEqual(
            models.Experiment.objects.count(),
            n_experiments
        )
        self.assertEqual(
            models.Pixel.objects.count(),
            n_pixels_per_set * n_pixel_sets
        )

        expected_output = (
            'Will generate {} experiments and {} pixel sets with {} '
            'pixels each…\n'
            'Successfully generated fixtures'
        ).format(
            n_experiments,
            n_pixel_sets,
            n_pixels_per_set
        )
        self.assertIn(expected_output, output.getvalue())
