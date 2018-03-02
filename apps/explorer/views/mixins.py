from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.gzip import gzip_page
from django.views.generic.edit import FormMixin
from gviz_api import DataTable

from ..forms import PixelSetSubsetSelectionForm
from ..utils import get_queryset_filtered_by_search_terms

from .helpers import set_search_terms_to_session


class DataTableMixin(object):

    def get_search_terms(self, session, **kwargs):

        raise NotImplementedError(_('You should define `get_search_terms()`'))

    def get_headers(self):

        raise NotImplementedError(_('You should define `get_headers()`'))

    def get_pixels_queryset(self):

        raise NotImplementedError(
            _('You should define `get_pixels_queryset()`')
        )

    def get_columns(self):

        return list(self.get_headers().keys())

    @method_decorator(gzip_page)
    def get(self, request, *args, **kwargs):

        if not request.is_ajax():
            raise SuspiciousOperation(
                'This endpoint should only be called from JavaScript.'
            )

        search_terms = self.get_search_terms(request.session)

        qs = get_queryset_filtered_by_search_terms(
            self.get_pixels_queryset(),
            search_terms=search_terms
        )

        dt = DataTable(self.get_headers())
        dt.LoadData(qs.values(*self.get_columns()))

        return HttpResponse(dt.ToJSon(), content_type='application/json')


class SubsetSelectionMixin(FormMixin):

    form_class = PixelSetSubsetSelectionForm

    def get_search_terms(self, session, **kwargs):

        raise NotImplementedError(_('You should define `get_search_terms()`'))

    def get_initial(self):

        initial = super().get_initial()

        initial.update({
            'search_terms': ' '.join(
                self.get_search_terms(self.request.session)
            )
        })
        return initial

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            set_search_terms_to_session(
                request.session,
                key=self.search_terms_session_key,
                search_terms=form.cleaned_data['search_terms']
            )

            return self.form_valid(form)
        else:
            # We should never reach this code because the form should always be
            # valid (no required field or validation)
            return self.form_invalid(form)  # pragma: no cover
