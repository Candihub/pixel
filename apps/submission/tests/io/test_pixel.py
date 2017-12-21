from pathlib import Path

from django.test import TestCase

from apps.core.factories import (
    NOTEBOOK_DEFAULT_PATH, SECONDARY_DATA_DEFAULT_PATH, AnalysisFactory,
    OmicsUnitFactory, OmicsUnitTypeFactory, PixelFactory, StrainFactory
)
from apps.core.models import OmicsUnit, Pixel
from apps.data.factories import EntryFactory
from apps.data.io.cgd import ChrFeatureParser
from apps.data.models import Repository
from apps.submission.io.pixel import PixelSetParser
from ...exceptions import PixelSetParserError, PixelSetParserSaveError


class LoadCGDMixin(object):

    def _load_cgd_entries(self):

        cgd_path = Path(
            'apps/submission/fixtures/'
        ) / Path(
            'C_glabrata_CBS138_current_chromosomal_feature_required.tab'
        )
        cgd_parser = ChrFeatureParser(cgd_path)
        cgd_parser.parse()
        cgd_parser.save(ignore_aliases=False)


class PixelTestCase(LoadCGDMixin, TestCase):

    def setUp(self):

        self.pixelset_path = Path(
            'apps/submission/fixtures/dataset-0001/Pixel_C10.txt'
        )
        self.analysis = AnalysisFactory(
            secondary_data__from_path=SECONDARY_DATA_DEFAULT_PATH,
            notebook__from_path=NOTEBOOK_DEFAULT_PATH,
        )
        self.description = "lorem ipsum"
        self.omics_unit_type = OmicsUnitTypeFactory()
        self.strain = StrainFactory()

    def _create_pixel_from_set(self, pixelset):
        entry = EntryFactory(
            identifier='CAGL0K09834g',
            description=(
                'Ortholog(s) have role in response to salt stress and '
                'cytoplasm localization'
            ),
            url=(
                'http://www.candidagenome.org/cgi-bin/locus.pl?dbid=/'
                'CAL0134577'
            ),
            repository=Repository.objects.get(name='CGD')
        )
        omics_unit = OmicsUnitFactory(
            reference=entry,
            strain=self.strain,
            type=self.omics_unit_type,
        )
        return PixelFactory(
            value=4.2,
            quality_score=0.8,
            omics_unit=omics_unit,
            pixel_set=pixelset,
        )

    def test_init(self):

        pixelset = PixelSetParser(self.pixelset_path)

        self.assertEqual(pixelset.pixelset_path, self.pixelset_path)
        self.assertIsNone(pixelset.pixels)

    def test_parse(self):

        pixelset = PixelSetParser(self.pixelset_path)
        pixelset.parse()

        self.assertIsNotNone(pixelset.pixels)
        self.assertEqual(len(pixelset.pixels), 1936)

        pixel = pixelset.pixels.loc['CAGL0F02695g', ]
        self.assertAlmostEqual(pixel.Value, 4.25954345565357)
        self.assertAlmostEqual(pixel.Quality_score, 5.0188163324757298e-5)

    def test_parse_with_force(self):

        pixelset = PixelSetParser(self.pixelset_path)
        self.assertIsNone(pixelset.pixels)

        pixelset.parse()
        self.assertIsNotNone(pixelset.pixels)

        old_pixels = pixelset.pixels
        pixelset.parse()
        self.assertEqual(id(pixelset.pixels), id(old_pixels))

        pixelset.parse(force=True)
        self.assertNotEqual(id(pixelset.pixels), id(old_pixels))

    def test_filter(self):

        pixelset = PixelSetParser(self.pixelset_path)

        self.assertEqual(pixelset.filter(), tuple([None] * 3))

        pixelset.parse()
        pixels, na, fuzzy = pixelset.filter()

        self.assertEqual(len(pixels), 1837)
        self.assertEqual(pixels.index[0], 'CAGL0F02695g')
        self.assertEqual(pixels.index[-1], 'CAGL0L01925g')

        self.assertEqual(len(na), 74)
        self.assertEqual(na.index[0], 'CAGL0C02475g')
        self.assertEqual(na.index[-1], 'CAGL0M12749g')

        self.assertEqual(len(fuzzy), 25)
        self.assertEqual(fuzzy.index[0], 'CAGL0A02211g;CAGL0D02640g')
        self.assertEqual(fuzzy.index[-1], 'CAGL0G08173g;CAGL0D05082g')

    def test_na_filter(self):

        pixelset = PixelSetParser(self.pixelset_path)
        pixelset.parse()
        pixels, na, fuzzy = pixelset.filter(na_filter=False)

        self.assertEqual(len(pixels), 1911)
        self.assertEqual(pixels.index[0], 'CAGL0F02695g')
        self.assertEqual(pixels.index[-1], 'CAGL0M12749g')

    def test_fuzzy_filter(self):

        pixelset = PixelSetParser(self.pixelset_path)
        pixelset.parse()
        pixels, na, fuzzy = pixelset.filter(fuzzy_filter=False)

        self.assertEqual(len(pixels), 1862)
        self.assertEqual(pixels.index[0], 'CAGL0F02695g')
        self.assertEqual(pixels.index[-1], 'CAGL0L01925g')

    def test__set_pixel_set(self):

        parser = PixelSetParser(self.pixelset_path)
        with self.assertRaises(PixelSetParserError):
            parser._set_pixel_set()

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
        )
        parser._set_pixel_set()
        pixelset = parser.pixelset
        self.assertIsNotNone(pixelset)
        self.assertEqual(pixelset.pixels_file.name, self.pixelset_path.name)
        self.assertEqual(pixelset.description, self.description)
        self.assertEqual(pixelset.analysis, self.analysis)

    def test__get_omics_units(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
        )
        with self.assertRaises(PixelSetParserSaveError):
            parser._get_omics_units(None)

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            strain=self.strain,
        )
        with self.assertRaises(PixelSetParserSaveError):
            parser._get_omics_units(None)

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
        )
        with self.assertRaises(PixelSetParserSaveError):
            parser._get_omics_units(None)

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )
        parser.parse()
        pixels, _, _ = parser.filter()

        # We need to load Entries first!
        self.assertEqual(OmicsUnit.objects.count(), 0)
        with self.assertRaises(PixelSetParserSaveError):
            parser._get_omics_units(pixels)
        self.assertEqual(OmicsUnit.objects.count(), 0)

        # So… load entries
        self._load_cgd_entries()

        # Then create omics units
        omics_units = parser._get_omics_units(pixels, verbose=True)
        self.assertEqual(omics_units.count(), 1837)
        self.assertEqual(OmicsUnit.objects.count(), 1837)

    def test__to_pixels(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )

        # With no pixel file parsed, _to_pixels has no effect
        parser._to_pixels()
        self.assertEqual(
            parser.db_pixels,
            {
                'new': [],
                'update': [],
            }
        )

        parser.parse()
        self._load_cgd_entries()
        parser._to_pixels()
        self.assertEqual(len(parser.db_pixels['new']), 1837)
        self.assertEqual(len(parser.db_pixels['update']), 0)

        db_pixel = parser.db_pixels['new'][0]
        pixel = parser.pixels.ix[db_pixel.omics_unit.reference.identifier]

        self.assertEqual(db_pixel.value, pixel.Value)
        self.assertEqual(db_pixel.quality_score, pixel.Quality_score)

    def test__to_pixels_with_existing_pixel(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )

        parser.parse()
        parser._set_pixel_set()
        self._load_cgd_entries()

        existing_db_pixel = self._create_pixel_from_set(parser.pixelset)

        parser._to_pixels()
        self.assertEqual(len(parser.db_pixels['new']), 1836)
        self.assertEqual(len(parser.db_pixels['update']), 1)

        # We should have updated existing pixel data
        identifier = existing_db_pixel.omics_unit.reference.identifier
        pixel = parser.pixels.ix[identifier]
        updated_db_pixel = parser.db_pixels['update'][0]
        self.assertEqual(updated_db_pixel.value, pixel.Value)
        self.assertEqual(updated_db_pixel.quality_score, pixel.Quality_score)

    def test_save(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )
        parser.parse()
        self._load_cgd_entries()

        self.assertEqual(Pixel.objects.count(), 0)
        parser.save()
        self.assertEqual(Pixel.objects.count(), 1837)

    def test_save_with_existing_pixel(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )
        parser.parse()
        parser._set_pixel_set()
        self._load_cgd_entries()

        self._create_pixel_from_set(parser.pixelset)
        self.assertEqual(Pixel.objects.count(), 1)
        parser.save()
        self.assertEqual(Pixel.objects.count(), 1837)

    def test_save_with_update(self):

        parser = PixelSetParser(
            self.pixelset_path,
            description=self.description,
            analysis=self.analysis,
            omics_unit_type=self.omics_unit_type,
            strain=self.strain,
        )
        parser.parse()
        parser._set_pixel_set()
        self._load_cgd_entries()

        pixel = self._create_pixel_from_set(parser.pixelset)
        self.assertEqual(Pixel.objects.count(), 1)
        self.assertEqual(pixel.value, 4.2)
        self.assertEqual(pixel.quality_score, 0.8)

        parser.save(update=True)
        self.assertEqual(Pixel.objects.count(), 1837)

        pixel = Pixel.objects.get(pk=pixel.pk)
        self.assertEqual(pixel.value, 2.703695974165)
        self.assertEqual(pixel.quality_score, 0.00268822352590468)
