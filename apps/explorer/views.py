from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin

from apps.core.models import OmicsArea, PixelSet, Tag
from .forms import (PixelSetFiltersForm, PixelSetExportForm,
                    PixelSetExportPixelsForm)
from .utils import export_pixelsets, export_pixels


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

            parent_omics_areas = form.cleaned_data.get('omics_areas')
            if parent_omics_areas:
                omics_areas = OmicsArea.objects.get_queryset_descendants(
                    parent_omics_areas,
                    include_self=True
                )
                qs = qs.filter(
                    analysis__experiments__omics_area__id__in=omics_areas
                )

            parent_tags = form.cleaned_data.get('tags')
            if parent_tags:
                # Add descendants to the tags queryset
                tags = Tag.objects.filter(
                    id__in=parent_tags
                ).with_descendants()

                qs = qs.filter(
                    Q(analysis__tags__id__in=tags) |
                    Q(analysis__experiments__tags__id__in=tags)
                )

            search = form.cleaned_data.get('search')
            if len(search):
                qs = qs.filter(
                    Q(analysis__experiments__description__icontains=search) |
                    Q(analysis__description__icontains=search) |
                    Q(pixel__omics_unit__reference__identifier__iexact=search)
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


class PixelSetDetailView(LoginRequiredMixin, FormMixin, DetailView):

    form_class = PixelSetExportPixelsForm
    http_method_names = ['get', 'post']
    model = PixelSet
    pixels_limit = 100
    template_name = 'explorer/pixelset_detail.html'

    def get_omics_units(self):

        return self.request.session.get('omics_units', [])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        qs = self.object.pixels.prefetch_related('omics_unit__reference')
        omics_units = self.get_omics_units()

        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        pixels = qs[:self.pixels_limit]

        context.update({
            'pixels': pixels,
            'pixels_limit': self.pixels_limit,
        })
        return context

    def get_initial(self):

        initial = super().get_initial()

        initial.update({
            'omics_units': ' '.join(self.get_omics_units()),
        })
        return initial

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            omics_units = form.cleaned_data['omics_units']
            request.session['omics_units'] = omics_units

            return self.form_valid(form)
        else:
            # We should never reach this code because the form should always be
            # valid (no required field or validation)
            return self.form_invalid(form)  # pragma: no cover

    def get_success_url(self):

        return self.object.get_absolute_url()


class PixelSetExportPixelsView(LoginRequiredMixin, BaseDetailView):

    ATTACHEMENT_FILENAME = 'pixels_{date_time}.csv'

    model = PixelSet

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportPixelsView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def get(self, request, *args, **kwargs):
        omics_units = request.session.get('omics_units', default=[])

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
