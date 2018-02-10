from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormMixin
from gviz_api import DataTable

from ..forms import PixelSetSubsetSelectionForm

from .helpers import get_omics_units_from_session


class DataTableMixin(object):

    def get_headers(self):

        raise NotImplementedError(_('You should define `get_headers()`'))

    def get_columns(self):

        return list(self.get_headers().keys())

    def get(self, request, *args, **kwargs):

        if not request.is_ajax():
            raise SuspiciousOperation(
                'This endpoint should only be called from JavaScript.'
            )

        qs = self.get_pixels_queryset()

        omics_units = get_omics_units_from_session(request.session)
        # we only filter by Omics Units when specified.
        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        dt = DataTable(self.get_headers())
        dt.LoadData(qs.values(*self.get_columns()))

        return HttpResponse(dt.ToJSon(), content_type='application/json')


class SubsetSelectionMixin(FormMixin):

    form_class = PixelSetSubsetSelectionForm

    def get_omics_units(self):

        return get_omics_units_from_session(self.request.session)

    def get_initial(self):

        initial = super().get_initial()

        initial.update({
            'omics_units': ' '.join(self.get_omics_units()),
        })
        return initial

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            omics_units = form.cleaned_data['omics_units']
            request.session.update({
                'explorer': {
                    'pixels': {
                        'omics_units': omics_units,
                    },
                },
            })

            return self.form_valid(form)
        else:
            # We should never reach this code because the form should always be
            # valid (no required field or validation)
            return self.form_invalid(form)  # pragma: no cover
