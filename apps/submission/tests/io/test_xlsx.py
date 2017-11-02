import pytest

from django.test import TestCase
from openpyxl import load_workbook

from apps.submission.io.xlsx import generate_template


class PixelIOXLSXTestCase(TestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_generate_template(self):

        pixel_template = self.tmpdir.join('pixel-template.xlsx')
        generate_template(output_file=pixel_template)

        wb = load_workbook(pixel_template)
        ws = wb.active

        assert ws.title == 'Import information for Pixel'
        assert ws['A1'].value == 'Experiment'
        assert ws['A3'].value == 'Omics area'
        assert ws['A4'].value == 'Completion date'
        assert ws['A5'].value == 'Summary'
        assert ws['A6'].value == 'Release date'
        assert ws['A7'].value == 'Data source'
        assert ws['A8'].value == 'Reference (entry)'
        assert ws['A10'].value == 'Analysis'
        assert ws['A12'].value == 'Name of secondary data file'
        assert ws['A13'].value == 'Name of notebook file'
        assert ws['A14'].value == 'Description'
        assert ws['A15'].value == 'Date of the analysis'
        assert ws['A17'].value == 'Pixel datasets'
        assert ws['A19'].value == 'File name'
        assert ws['B19'].value == 'Omics Unit type'
        assert ws['C19'].value == 'Strain (Species)'
        assert ws['D19'].value == 'Comment'
