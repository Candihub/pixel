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
