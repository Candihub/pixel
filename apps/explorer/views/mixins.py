from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.gzip import gzip_page
from django.views.generic.edit import FormMixin
from gviz_api import DataTable

from ..forms import PixelSetSubsetSelectionForm

from .helpers import get_omics_units_from_session, set_omics_units_to_session


class DataTableMixin(object):

    def get_omics_units(self, session, **kwargs):

        raise NotImplementedError(_('You should define `get_omics_units()`'))

    def get_headers(self):

        raise NotImplementedError(_('You should define `get_headers()`'))

    def get_columns(self):

        return list(self.get_headers().keys())

    @method_decorator(gzip_page)
    def get(self, request, *args, **kwargs):

        if not request.is_ajax():
            raise SuspiciousOperation(
                'This endpoint should only be called from JavaScript.'
            )

        qs = self.get_pixels_queryset()

        omics_units = self.get_omics_units(request.session)

        # we only filter by Omics Units when specified.
        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        dt = DataTable(self.get_headers())
        dt.LoadData(qs.values(*self.get_columns()))

        return HttpResponse(dt.ToJSon(), content_type='application/json')


class SubsetSelectionMixin(FormMixin):

    form_class = PixelSetSubsetSelectionForm

    def get_omics_units(self, session, **kwargs):

        raise NotImplementedError(_('You should define `get_omics_units()`'))

    def get_initial(self):

        initial = super().get_initial()

        initial.update({
            'omics_units': ' '.join(self.get_omics_units(self.request.session))
        })
        return initial

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            set_omics_units_to_session(
                request.session,
                key=self.omics_units_session_key,
                omics_units=form.cleaned_data['omics_units']
            )

            return self.form_valid(form)
        else:
            # We should never reach this code because the form should always be
            # valid (no required field or validation)
            return self.form_invalid(form)  # pragma: no cover


class GetOmicsUnitsMixin(object):

    omics_units_session_key = 'pixelset_selection_omics_units'

    def get_omics_units(self, session, **kwargs):

        return get_omics_units_from_session(
            session,
            key=self.omics_units_session_key,
            **kwargs
        )
