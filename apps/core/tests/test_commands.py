from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from ..management.commands.make_development_fixtures import DEFAULT_N_PIXELSETS
from ..models import PixelSet


@override_settings(DEBUG=True)
class MakeDevelopmentFixturesCommandTestCase(TestCase):

    def test_command(self):

        output = StringIO()

        with self.settings(DEBUG=False):
            with self.assertRaises(CommandError):
                call_command('make_development_fixtures', stdout=output)

        self.assertEqual(PixelSet.objects.count(), 0)
        call_command('make_development_fixtures', stdout=output)
        self.assertEqual(PixelSet.objects.count(), DEFAULT_N_PIXELSETS)

        expected_output = (
            'Will generate {} pixel sets…\n'
            'Successfully generated fixtures'
        ).format(DEFAULT_N_PIXELSETS)
        self.assertIn(expected_output, output.getvalue())

    def test_command_with_custom_pixelset(self):

        output = StringIO()

        n_pixel_sets = 5
        self.assertEqual(PixelSet.objects.count(), 0)
        call_command(
            'make_development_fixtures',
            pixel_sets=n_pixel_sets,
            stdout=output
        )
        self.assertEqual(PixelSet.objects.count(), n_pixel_sets)
