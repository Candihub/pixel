from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic.detail import BaseDetailView

from apps.core.models import PixelSet

from ..utils import export_pixels

from .helpers import get_omics_units_from_session
from .mixins import DataTableMixin, SubsetSelectionMixin


class DataTableDetailView(LoginRequiredMixin, DataTableMixin, BaseDetailView):

    model = PixelSet

    def get_pixels_queryset(self):

        return self.get_object().pixels


class PixelSetDetailValuesView(DataTableDetailView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetDetailQualityScoresView(DataTableDetailView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}


class PixelSetDetailView(LoginRequiredMixin, SubsetSelectionMixin, DetailView):

    http_method_names = ['get', 'post']
    model = PixelSet
    pixels_limit = 100
    template_name = 'explorer/pixelset_detail.html'

    def get_queryset(self):

        qs = super().get_queryset().select_related(
            'analysis__pixeler',
        )

        return qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        qs = self.object.pixels.select_related('omics_unit__reference')

        omics_units = self.get_omics_units()

        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        pixels = qs[:self.pixels_limit]

        context.update({
            'pixels': pixels,
            'pixels_count': qs.count(),
            'pixels_limit': self.pixels_limit,
            'total_count': self.object.pixels.count(),
            'pixelset_experiments': self.object.analysis.experiments.all(),
        })
        return context

    def get_success_url(self):

        return self.get_object().get_absolute_url()


class PixelSetExportPixelsView(LoginRequiredMixin, BaseDetailView):

    ATTACHEMENT_FILENAME = 'pixels_{date_time}.csv'

    model = PixelSet

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportPixelsView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def get(self, request, *args, **kwargs):
        omics_units = get_omics_units_from_session(request.session)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )

        export_pixels(
            self.get_object(),
            omics_units=omics_units,
            output=response
        )

        return response
