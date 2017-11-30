from pathlib import Path

from django.test import TestCase

from apps.submission.io.pixel import PixelSetParser


class PixelTestCase(TestCase):

    def setUp(self):

        self.pixelset_path = Path(
            'apps/submission/fixtures/dataset-0001/Pixel_C10.txt'
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
