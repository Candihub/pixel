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

    def test_entry_identifier_Not_None(self):
        self.assertEqual(
            self.Strain_admin.entry_identifier(self.Strain),
            self.Strain.reference.identifier
        )

    def test_entry_identifier_None(self):
        self.Strain.reference = None
        self.assertEqual(
            self.Strain_admin.entry_identifier(self.Strain),
            "-"
        )


class PixelAdminTestCase(TestCase):

    def setUp(self):
        site = AdminSite()
        self.Pixel = factories.PixelFactory()
        self.Pixel_admin = admin.PixelAdmin(models.Pixel, site)

    def test_get_analysis(self):
        self.assertEqual(
            self.Pixel_admin.get_analysis(self.Pixel),
            self.Pixel.analysis.description
        )
