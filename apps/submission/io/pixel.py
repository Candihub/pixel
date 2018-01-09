import logging

import pandas

from django.utils.translation import ugettext as _

from apps.core.models import OmicsUnit, Pixel, PixelSet
from apps.data.models import Entry
from ..exceptions import PixelSetParserError, PixelSetParserSaveError

logger = logging.getLogger(__name__)


class PixelSetParser(object):

    def __init__(self,
                 pixelset_path,
                 description=None,
                 analysis=None,
                 omics_unit_type=None,
                 strain=None):

        self.pixelset = None
        self.pixelset_path = pixelset_path
        self.description = description
        self.analysis = analysis
        self.omics_unit_type = omics_unit_type
        self.strain = strain
        self.pixels = None
        self.db_pixels = {
            'new': [],
            'update': [],
        }

    def parse(self, force=False):

        if self.pixels is not None and not force:
            logger.debug(
                'Aborting because pixels have already been parsed and '
                'force = False'
            )
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

    def _set_pixel_set(self):

        if self.analysis is None:
            raise PixelSetParserError(
                _(
                    "You need to define PixelSetParser.analysis to get or "
                    "create a PixelSet"
                )
            )

        logger.debug(
            "Will set PixelSet for file: {}".format(self.pixelset_path.name)
        )

        self.pixelset, __ = PixelSet.objects.get_or_create(
            pixels_file__exact=self.pixelset_path.name,
            description=self.description,
            analysis=self.analysis,
        )
        # Get or create cannot set file path as is
        self.pixelset.pixels_file.name = self.pixelset_path.name
        self.pixelset.save()

    def _get_omics_units(self, pixels, verbose=False):

        if any((self.strain is None, self.omics_unit_type is None)):
            raise PixelSetParserSaveError(
                _(
                    "You need to define PixelSetParser.strain and "
                    "PixelSetParser.omics_unit_type to get omics units"
                )
            )

        identifiers = pixels.axes[0].tolist()
        existing = OmicsUnit.objects.filter(
            strain=self.strain,
            type=self.omics_unit_type
        ).values_list('reference__identifier', flat=True)

        to_create = [
            p for p in identifiers if p not in existing
        ]

        related_entries = Entry.objects.filter(identifier__in=to_create)

        if related_entries.count() != len(to_create):
            raise PixelSetParserSaveError(
                _(
                    "Required entries partially exists ({} vs {}). Please "
                    "load entries first thanks to the load_entries management "
                    "command."
                ).format(
                    related_entries.count(),
                    len(to_create)
                )
            )

        omics_units = []
        for entry in related_entries:
            omics_units.append(
                OmicsUnit(
                    reference=entry,
                    strain=self.strain,
                    type=self.omics_unit_type,
                )
            )
        OmicsUnit.objects.bulk_create(omics_units)

        return OmicsUnit.objects.filter(
            reference__identifier__in=identifiers
        )

    def _to_pixels(self):

        if self.pixels is None:
            return

        self._set_pixel_set()
        pixels, na, fuzzy = self.filter()

        # Pixels and OmicsUnits are sorted by OmicsUnit reference identifier
        omics_units = self._get_omics_units(pixels)

        # Look for existing Pixels
        identifiers = pixels.axes[0].tolist()
        existing = Pixel.objects.filter(
            omics_unit__reference__identifier__in=identifiers,
            pixel_set=self.pixelset,
        ).values_list(
            'omics_unit__reference__identifier',
            flat=True
        )

        for omics_unit in omics_units:
            identifier = omics_unit.reference.identifier
            pixel = pixels.ix[identifier]
            db_pixel = Pixel(
                value=pixel.Value,
                quality_score=pixel.Quality_score,
                omics_unit=omics_unit,
                pixel_set=self.pixelset,
            )
            if identifier in existing:
                self.db_pixels['update'].append(db_pixel)
            else:
                self.db_pixels['new'].append(db_pixel)

    def save(self, update=False):

        self._to_pixels()

        # Create news entries
        Pixel.objects.bulk_create(self.db_pixels['new'], batch_size=500)

        if not update:
            return

        # Update old entries
        for updated_pixel in self.db_pixels['update']:
            pixel = Pixel.objects.get(
                omics_unit=updated_pixel.omics_unit,
                pixel_set=updated_pixel.pixel_set
            )
            pixel.value = updated_pixel.value
            pixel.quality_score = updated_pixel.quality_score
            pixel.save(update_fields=['value', 'quality_score'])
