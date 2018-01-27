import re

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from apps.core.models import PixelSet
from .forms import (PixelSetFiltersForm, PixelSetExportForm,
                    PixelSetExportPixelsForm)
from .utils import export_pixelsets, export_pixels


def str_to_set(input):
    """Returns a set of strings by splitting the given `input` string on space,
    comma or new line. It eliminates duplicates and strips each string.
    """
    return set(
        # Remove (filter) empty string values
        filter(
            None,
            [part.strip() for part in re.split('\s*,\s*|\s+|\n', input)]
        )
    )


class PixelSetListView(LoginRequiredMixin, FormMixin, ListView):

    form_class = PixelSetFiltersForm
    model = PixelSet
    paginate_by = 10
    template_name = 'explorer/pixelset_list.html'

    def get_form_kwargs(self):

        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })

        return kwargs

    def get_queryset(self):

        qs = super().get_queryset()

        form = self.get_form()
        if form.is_valid():

            species = form.cleaned_data.get('species')
            if species:
                qs = qs.filter(
                    pixel__omics_unit__strain__species__id__in=species
                )

            omics_unit_types = form.cleaned_data.get('omics_unit_types')
            if omics_unit_types:
                qs = qs.filter(
                    pixel__omics_unit__type__id__in=omics_unit_types
                )

            omics_areas = form.cleaned_data.get('omics_areas')
            if omics_areas:
                qs = qs.filter(
                    analysis__experiments__omics_area__id__in=omics_areas
                )

            tags = form.cleaned_data.get('tags')
            if tags:
                qs = qs.filter(
                    Q(analysis__tags__id__in=tags) |
                    Q(analysis__experiments__tags__id__in=tags)
                )

            search = form.cleaned_data.get('search')
            if len(search):
                qs = qs.filter(
                    Q(analysis__experiments__description__contains=search) |
                    Q(analysis__description__contains=search) |
                    Q(pixel__omics_unit__reference__identifier__exact=search)
                )

        # optimize db queries
        qs = qs.select_related(
            'analysis',
            'analysis__pixeler',
        ).prefetch_related(
            'analysis__experiments__omics_area',
            'analysis__experiments__tags',
            'analysis__tags',
            'pixels__omics_unit__type',
            'pixels__omics_unit__strain__species',
        )

        return qs.distinct()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update({
            'export_form': PixelSetExportForm(),
        })
        return context


class PixelSetExportView(LoginRequiredMixin, FormView):
    ATTACHEMENT_FILENAME = 'pixelsets_{date_time}.zip'

    form_class = PixelSetExportForm

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def form_valid(self, form):

        content = export_pixelsets(form.cleaned_data['pixel_sets']).getvalue()

        response = HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )
        return response

    def form_invalid(self, form):

        messages.error(
            self.request,
            "\n".join([
                errors[0].message for errors in form.errors.as_data().values()
            ])
        )

        redirect_to = self.request.POST.get(
            'redirect_to',
            reverse('explorer:pixelset_list')
        )
        return HttpResponseRedirect(redirect_to)


class PixelSetDetailView(LoginRequiredMixin, DetailView):

    model = PixelSet
    template_name = 'explorer/pixelset_detail.html'
    pixels_limit = 100

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        pixels = self.object.pixels.prefetch_related(
            'omics_unit__reference'
        )[:self.pixels_limit]

        context.update({
            'pixels': pixels,
            'pixels_limit': self.pixels_limit,
            'export_form': PixelSetExportPixelsForm(),
        })
        return context


class PixelSetExportPixelsView(LoginRequiredMixin,
                               SingleObjectMixin,
                               FormView):
    ATTACHEMENT_FILENAME = 'pixels_{date_time}.zip'

    form_class = PixelSetExportPixelsForm
    model = PixelSet

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportPixelsView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def form_valid(self, form):

        omics_units = str_to_set(form.cleaned_data['omics_units'])

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

    def form_invalid(self, form):

        messages.error(self.request, _('You must select a subset of pixels.'))

        return HttpResponseRedirect(self.get_object().get_absolute_url())
