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
        self.sgd_file = Path(
            'apps/data/fixtures/'
        ) / Path(
            'SGD_feature_S000002143.tab'
        )

    def test_command_without_args(self):

        with self.assertRaises(CommandError):
            call_command('load_entries', stdout=StringIO())

    def test_command_with_invalid_database(self):

        args = ['path/to/file.tab', '--database', 'INVALID']

        with self.assertRaises(CommandError):
            call_command('load_entries', *args, stdout=StringIO())

    def test_command_load_cgd_file(self):

        output = StringIO()
        args = [self.cgd_file, '--database', 'CGD']

        self.assertEqual(Entry.objects.count(), 0)
        call_command(
            'load_entries',
            *args,
            stdout=output
        )
        self.assertEqual(Entry.objects.count(), 30)

        expected_output = 'Successfully imported file: {}'.format(
            self.cgd_file
        )
        self.assertIn(expected_output, output.getvalue())

    def test_command_load_sgd_file(self):

        output = StringIO()
        args = [self.sgd_file, '--database', 'SGD']

        self.assertEqual(Entry.objects.count(), 0)
        call_command(
            'load_entries',
            *args,
            stdout=output
        )
        self.assertEqual(Entry.objects.count(), 11)

        expected_output = 'Successfully imported file: {}'.format(
            self.sgd_file
        )
        self.assertIn(expected_output, output.getvalue())

    def test_command_load_cgd_file_without_aliases(self):

        output = StringIO()
        args = [self.cgd_file, '--database', 'CGD']

        self.assertEqual(Entry.objects.count(), 0)
        call_command(
            'load_entries',
            *args,
            ignore_aliases=True,
            stdout=output
        )
        self.assertEqual(Entry.objects.count(), 10)

        expected_output = 'Successfully imported file: {}'.format(
            self.cgd_file
        )
        self.assertIn(expected_output, output.getvalue())

    def test_command_load_sgd_file_without_aliases(self):

        output = StringIO()
        args = [self.sgd_file, '--database', 'SGD']

        self.assertEqual(Entry.objects.count(), 0)
        call_command(
            'load_entries',
            *args,
            ignore_aliases=True,
            stdout=output
        )
        self.assertEqual(Entry.objects.count(), 9)

        expected_output = 'Successfully imported file: {}'.format(
            self.sgd_file
        )
        self.assertIn(expected_output, output.getvalue())
