from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.urls.base import reverse
from django.views.generic import TemplateView, View
from django.views.generic.detail import BaseDetailView

from apps.core.models import Pixel, PixelSet

from ..utils import create_html_table_for_pixelsets

from .helpers import (
    get_omics_units_from_session, get_selected_pixel_sets_from_session
)
from .mixins import DataTableMixin, SubsetSelectionMixin


class GetOmicsUnitsMixin(object):

    omics_units_session_key = 'pixelset_selection_omics_units'

    def get_omics_units(self, session, **kwargs):

        return get_omics_units_from_session(
            session,
            key=self.omics_units_session_key,
            **kwargs
        )


class DataTableCumulativeView(LoginRequiredMixin, GetOmicsUnitsMixin,
                              DataTableMixin,
                              View):

    def get_pixels_queryset(self):

        selected_pixelset_ids = get_selected_pixel_sets_from_session(
            self.request.session
        )

        return Pixel.objects.filter(pixel_set_id__in=selected_pixelset_ids)


class PixelSetSelectionCumulativeValuesView(DataTableCumulativeView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetSelectionCumulativeQualityScoresView(DataTableCumulativeView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}


class DataTableSelectionView(LoginRequiredMixin, GetOmicsUnitsMixin,
                             DataTableMixin,
                             BaseDetailView):

    model = PixelSet

    def get_pixels_queryset(self):

        return self.get_object().pixels


class PixelSetSelectionValuesView(DataTableSelectionView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetSelectionQualityScoresView(DataTableSelectionView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}


class PixelSetSelectionView(LoginRequiredMixin, GetOmicsUnitsMixin,
                            SubsetSelectionMixin,
                            TemplateView):

    omics_units_limit = 100
    template_name = 'explorer/pixelset_selection.html'

    def get(self, request, *args, **kwargs):

        selection = get_selected_pixel_sets_from_session(request.session)

        if not len(selection):
            return self.empty_selection(request)

        return super().get(request, *args, **kwargs)

    def empty_selection(self, request):

        messages.error(
            request,
            _("Cannot explore an empty selection.")
        )

        return HttpResponseRedirect(reverse('explorer:pixelset_list'))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        selected_pixelset_ids = get_selected_pixel_sets_from_session(
            self.request.session
        )

        selected_pixelsets = PixelSet.objects.filter(
            id__in=selected_pixelset_ids
        )

        qs = Pixel.objects.filter(
            pixel_set_id__in=selected_pixelsets
        ).select_related(
            'omics_unit__reference'
        )

        omics_units = self.get_omics_units(self.request.session)

        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        pixels_count = qs.count()

        total_count = Pixel.objects.filter(
            pixel_set_id__in=selected_pixelsets
        ).count()

        html_table = create_html_table_for_pixelsets(
            selected_pixelset_ids,
            omics_units=omics_units,
            # we do not display all the data
            display_limit=self.omics_units_limit,
        )

        context.update({
            'html_table': html_table,
            'omics_units_limit': self.omics_units_limit,
            'selected_pixelsets': selected_pixelsets,
            'pixels_count': pixels_count,
            'total_count': total_count,
        })
        return context

    def get_success_url(self):

        return reverse('explorer:pixelset_selection')
