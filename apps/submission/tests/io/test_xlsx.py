from pathlib import Path

import pytest
from django.test import TestCase
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Alignment, Border, Color, Font, PatternFill, Side, colors
)

from apps.submission.io.xlsx import (
    XLSX_CHECKSUM, generate_template, sha256_checksum, style_range
)


def test_style_range():

    wb = Workbook()
    ws = wb.active
    start = 1
    stop = 10
    column = 'A'
    cell_range = f'{column}{start}:{column}{stop}'

    # Border
    dashed_bottom_border = Border(bottom=Side(style='dashed'))
    style_range(ws, cell_range, border=dashed_bottom_border)
    cell = f'{column}{start}'
    assert ws[cell].border.top == dashed_bottom_border.top
    cell = f'{column}{stop}'
    assert ws[cell].border.bottom == dashed_bottom_border.bottom

    # Fill
    red_fill = PatternFill('solid', fgColor=colors.RED)
    style_range(ws, cell_range, fill=red_fill)
    for row in range(start, stop + 1):
        cell = f'{column}{row}'
        assert ws[cell].fill == red_fill

    # Font
    blue_font = Font(color=colors.BLUE)
    style_range(ws, cell_range, font=blue_font)
    for row in range(start, stop + 1):
        cell = f'{column}{row}'
        assert ws[cell].font == blue_font

    # Alignment
    center_vertical_alignment = Alignment(vertical='center')
    style_range(ws, cell_range, alignment=center_vertical_alignment)
    for row in range(start, stop + 1):
        cell = f'{column}{row}'
        assert ws[cell].alignment == center_vertical_alignment


def test_sha256_checksum():

    meta_filename = Path('apps/submission/fixtures/meta.xlsx')
    checksum = sha256_checksum(meta_filename)
    assert checksum == XLSX_CHECKSUM


class XLSXTemplateTestCase(TestCase):

    fixtures = [
        'apps/data/fixtures/initial_data.json',
        'apps/core/fixtures/initial_data.json',
    ]

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_generate_template(self):

        pixel_template = self.tmpdir.join('pixel-template.xlsx')
        checksum = generate_template(filename=pixel_template)

        assert checksum == XLSX_CHECKSUM

        wb = load_workbook(pixel_template)
        ws = wb.active

        # fields
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

        # user data
        user_data_cells = tuple(
            f'B{r}' for r in list(range(3, 9)) + list(range(12, 16))
        ) + tuple(
            f'{c}{r}' for r in range(20, 31) for c in ('A', 'B', 'C', 'D')
        )
        expected_user_data_fg_color = Color('fdffd9')
        for cell in user_data_cells:
            assert ws[cell].fill.fgColor == expected_user_data_fg_color
