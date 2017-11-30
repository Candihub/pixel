import pandas


class PixelSetParser(object):

    def __init__(self, pixelset_path):

        self.pixelset_path = pixelset_path
        self.pixels = None

    def parse(self, force=False):

        if self.pixels is not None and not force:
            return

        self.pixels = pandas.read_csv(
            self.pixelset_path,
            delim_whitespace=True,
            index_col=0
        )

    def filter(self, na_filter=True, fuzzy_filter=True):

        if self.pixels is None:
            return None, None, None

        pixels = self.pixels
        na = pixels[pixels.isna().any(axis=1)]
        fuzzy = pixels.filter(like=';', axis=0)

        if na_filter:
            pixels = pixels.dropna()

        if fuzzy_filter:
            pixels = pixels.loc[pixels.index.drop(fuzzy.index), :]

        return pixels, na, fuzzy
