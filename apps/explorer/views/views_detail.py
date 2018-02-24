from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import DetailView
from django.views.generic.detail import BaseDetailView
from apps.core.models import PixelSet

from ..utils import export_pixels, get_queryset_filtered_by_search_terms

from .helpers import get_search_terms_from_session, set_search_terms_to_session
from .mixins import DataTableMixin, SubsetSelectionMixin


class GetSearchTermsMixin(object):

    search_terms_session_key = 'pixelset_detail_search_terms'

    def get_search_terms(self, session, **kwargs):

        return get_search_terms_from_session(
            session,
            key=self.search_terms_session_key,
            **kwargs
        )


class DataTableDetailView(LoginRequiredMixin, GetSearchTermsMixin,
                          DataTableMixin,
                          BaseDetailView):

    model = PixelSet

    def get_pixels_queryset(self):

        return self.get_object().pixels


class PixelSetDetailValuesView(DataTableDetailView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetDetailQualityScoresView(DataTableDetailView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}


class PixelSetDetailView(LoginRequiredMixin, GetSearchTermsMixin,
                         SubsetSelectionMixin,
                         DetailView):

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

        search_terms = self.get_search_terms(self.request.session)
        qs = get_queryset_filtered_by_search_terms(
            self.object.pixels.select_related('omics_unit__reference'),
            search_terms=search_terms
        )

        pixels = qs[:self.pixels_limit]

        context.update({
            'pixels': pixels,
            'pixels_count': qs.count(),
            'pixels_limit': self.pixels_limit,
            'search_terms': search_terms,
            'total_count': self.object.pixels.count(),
            'pixelset_experiments': self.object.analysis.experiments.all(),
        })
        return context

    def get_success_url(self):

        return self.get_object().get_absolute_url()


class PixelSetExportPixelsView(LoginRequiredMixin, GetSearchTermsMixin,
                               BaseDetailView):

    ATTACHEMENT_FILENAME = 'pixels_{date_time}.csv'

    model = PixelSet

    @staticmethod
    def get_export_archive_filename():

        return PixelSetExportPixelsView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def get(self, request, *args, **kwargs):

        search_terms = self.get_search_terms(request.session)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )

        export_pixels(
            self.get_object(),
            search_terms=search_terms,
            output=response
        )

        return response


class PixelSetDetailClearView(LoginRequiredMixin, BaseDetailView):

    http_method_names = ['post', ]
    model = PixelSet
    search_terms_session_key = 'pixelset_detail_search_terms'

    def post(self, request, *args, **kwargs):

        set_search_terms_to_session(
            request.session,
            key=self.search_terms_session_key,
            search_terms=[]
        )

        messages.success(request, _("The selection has been cleared."))

        return HttpResponseRedirect(
            request.POST.get(
                'redirect_to',
                self.get_object().get_absolute_url()
            )
        )
