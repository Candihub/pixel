import pytest

from django.test import TestCase

from apps.explorer.views.mixins import DataTableMixin, SubsetSelectionMixin


class DataTableMixinTestCase(TestCase):

    def test_get_search_terms_must_be_implemented(self):

        class DataTableWithNoGetSearchTerms(DataTableMixin):
            pass

        with pytest.raises(NotImplementedError):
            fake_session = dict()

            obj = DataTableWithNoGetSearchTerms()
            obj.get_search_terms(fake_session)


class SubsetSelectionMixinTestCase(TestCase):

    def test_get_search_terms_must_be_implemented(self):

        class SubsetSelectionWithNoGetSearchTerms(SubsetSelectionMixin):
            pass

        with pytest.raises(NotImplementedError):
            fake_session = dict()

            obj = SubsetSelectionWithNoGetSearchTerms()
            obj.get_search_terms(fake_session)
