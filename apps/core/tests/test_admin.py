from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from .. import admin
from .. import factories
from .. import models


class UUIDModelAdminMixinTestCase(TestCase):

    def test_get_short_uuid(self):

        omics_unit = factories.OmicsUnitFactory()
        mixin = admin.UUIDModelAdminMixin()

        self.assertEqual(mixin.get_short_uuid(omics_unit), str(omics_unit))


class TagsModelAdminMixinTestCase(TestCase):

    def test_get_tags(self):

        tags = 'foo/bar, lol'
        analysis = factories.AnalysisFactory(
            secondary_data__from_path=factories.SECONDARY_DATA_DEFAULT_PATH,
            notebook__from_path=factories.NOTEBOOK_DEFAULT_PATH,
        )
        analysis.tags = tags
        analysis.save()

        mixin = admin.TagsModelAdminMixin()

        self.assertEqual(mixin.get_tags(analysis), tags)


class OmicsUnitAdminTestCase(TestCase):

    def setUp(self):
        site = AdminSite()
        self.omics_unit = factories.OmicsUnitFactory()
        self.omics_unit_admin = admin.OmicsUnitAdmin(models.OmicsUnit, site)

    def test_get_species(self):

        self.assertEqual(
            self.omics_unit_admin.get_species(self.omics_unit),
            self.omics_unit.strain.species.name
        )

    def test_get_reference_identifier(self):

        self.assertEqual(
            self.omics_unit_admin.get_reference_identifier(self.omics_unit),
            self.omics_unit.reference.identifier
        )


class StrainAdminTestCase(TestCase):

    def setUp(self):
        site = AdminSite()
        self.Strain = factories.StrainFactory()
        self.Strain_admin = admin.StrainAdmin(models.Strain, site)

    def test_get_species(self):
        self.assertEqual(
            self.Strain_admin.get_species(self.Strain),
            self.Strain.species.name
        )

    def test_get_entry_identifier_with_reference(self):
        self.assertEqual(
            self.Strain_admin.get_entry_identifier(self.Strain),
            self.Strain.reference.identifier
        )

    def test_get_entry_identifier_without_reference(self):
        self.Strain.reference = None
        self.assertEqual(
            self.Strain_admin.get_entry_identifier(self.Strain),
            "-"
        )


class PixelAdminTestCase(TestCase):

    def setUp(self):
        site = AdminSite()
        analysis = factories.AnalysisFactory(
            secondary_data__from_path=factories.SECONDARY_DATA_DEFAULT_PATH,
            notebook__from_path=factories.NOTEBOOK_DEFAULT_PATH,
        )
        pixel_set = factories.PixelSetFactory(
            analysis=analysis,
            pixels_file__from_path=factories.PIXELS_DEFAULT_PATH,
        )
        self.Pixel = factories.PixelFactory(pixel_set=pixel_set)
        self.Pixel_admin = admin.PixelAdmin(models.Pixel, site)

    def test_get_analysis_description(self):
        self.assertEqual(
            self.Pixel_admin.get_analysis_description(self.Pixel),
            self.Pixel.pixel_set.analysis.description
        )
