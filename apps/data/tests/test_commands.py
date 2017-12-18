from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

from ..models import Entry


class LoadEntriesCommandTestCase(TestCase):

    def setUp(self):

        self.cgd_file = Path(
            'apps/data/fixtures/'
        ) / Path(
            'C_glabrata_CBS138_current_chromosomal_feature_10.tab'
        )

    def test_command(self):

        output = StringIO()

        with self.assertRaises(CommandError):
            call_command('load_entries', stdout=output)

        self.assertEqual(Entry.objects.count(), 0)
        call_command('load_entries', cgd=self.cgd_file, stdout=output)
        self.assertEqual(Entry.objects.count(), 10)

        expected_output = 'Successfully imported CGD file: {}'.format(
            self.cgd_file
        )
        self.assertIn(expected_output, output.getvalue())
