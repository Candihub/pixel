import pytest

from django.test import TestCase

from apps.explorer.views.mixins import DataTableMixin, SubsetSelectionMixin


class DataTableMixinTestCase(TestCase):

    def test_get_omics_units_must_be_implemented(self):

        class DataTableWithNoGetOmicsUnits(DataTableMixin):
            pass

        with pytest.raises(NotImplementedError):
            fake_session = dict()

            obj = DataTableWithNoGetOmicsUnits()
            obj.get_omics_units(fake_session)


class SubsetSelectionMixinTestCase(TestCase):

    def test_get_omics_units_must_be_implemented(self):

        class SubsetSelectionWithNoGetOmicsUnits(SubsetSelectionMixin):
            pass

        with pytest.raises(NotImplementedError):
            fake_session = dict()

            obj = SubsetSelectionWithNoGetOmicsUnits()
            obj.get_omics_units(fake_session)
