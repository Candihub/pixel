from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _, ngettext
from django.views.generic import (
    DetailView, FormView, ListView, RedirectView, View
)
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import FormMixin
from gviz_api import DataTable

from apps.core.models import OmicsArea, PixelSet, Tag
from .forms import (
    PixelSetFiltersForm, PixelSetExportForm, PixelSetExportPixelsForm,
    PixelSetSelectForm, SessionPixelSetSelectForm
)
from .utils import export_pixelsets, export_pixels


def get_omics_units_from_session(session, default=[]):
    return session.get(
        'export', {}
    ).get(
        'pixels', {}
    ).get(
        'omics_units', default
    )


def get_pixel_sets_for_export(session, default=[]):
    return session.get(
        'export', {}
    ).get(
        'pixelsets', default
    )


class DataTableView(BaseDetailView):

    model = PixelSet

    def get_headers(self):

        raise NotImplementedError(_('You should define `get_headers()`'))

    def get_columns(self):

        return list(self.get_headers().keys())

    def get(self, request, *args, **kwargs):

        if not request.is_ajax():
            raise SuspiciousOperation(
                'This endpoint should only be called from JavaScript.'
            )

        qs = self.get_object().pixels

        omics_units = get_omics_units_from_session(request.session)
        # we only filter by Omics Units when specified.
        if len(omics_units) > 0:
            qs = qs.filter(omics_unit__reference__identifier__in=omics_units)

        dt = DataTable(self.get_headers())
        dt.LoadData(qs.values(*self.get_columns()))

        return HttpResponse(dt.ToJSon(), content_type='application/json')


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
            'analysis__experiments__tags',
            'analysis__tags',
        )

        return qs.distinct()

    def get_context_data(self, **kwargs):

        selected_pixelset = get_pixel_sets_for_export(self.request.session)
        if len(selected_pixelset):
            selected_pixelset = PixelSet.objects.filter(
                id__in=selected_pixelset
            )

        context = super().get_context_data(**kwargs)
        context.update({
            'export_form': PixelSetExportForm(),
            'select_form': PixelSetSelectForm(),
            'selected_pixelsets': selected_pixelset,
        })
        return context


class PixelSetSelectionClearView(LoginRequiredMixin, RedirectView):

    http_method_names = ['post', ]

    def get_redirect_url(self, *args, **kwargs):
        return self.request.POST.get(
            'redirect_to',
            reverse('explorer:pixelset_list')
        )

    def post(self, request, *args, **kwargs):

        request.session.update({
            'export': {
                'pixelsets': []
            }
        })

        messages.success(
            request,
            _("Pixel Set selection has been cleared.")
        )

        return super().post(request, *args, **kwargs)


class PixelSetDeselectView(LoginRequiredMixin, FormView):

    form_class = SessionPixelSetSelectForm
    http_method_names = ['post', ]

    def get_success_url(self):
        return self.request.POST.get(
            'redirect_to',
            reverse('explorer:pixelset_list')
        )

    def get_form(self, form_class=None):
        """Instanciate the form with appropriate pixel set choices
        (i.e. pixel sets stored in session)
        """
        if form_class is None:
            form_class = self.get_form_class()

        session_pixel_sets = get_pixel_sets_for_export(self.request.session)

        return form_class(session_pixel_sets, **self.get_form_kwargs())

    def form_valid(self, form):

        session_pixel_sets = get_pixel_sets_for_export(self.request.session)
        pixel_set = form.cleaned_data['pixel_set']
        session_pixel_sets.remove(pixel_set)

        self.request.session.update({
            'export': {
                'pixelsets': session_pixel_sets
            }
        })

        messages.success(
            self.request,
            _("Pixel Set {} has been removed from selection.").format(
                pixel_set
            )
        )

        return super().form_valid(form)

    def form_invalid(self, form):

        messages.error(
            self.request,
            '\n'.join([
                f'{v[0]}' for (k, v) in form.errors.items()
            ])
        )

        return HttpResponseRedirect(self.get_success_url())


class PixelSetSelectView(LoginRequiredMixin, FormView):

    form_class = PixelSetSelectForm
    http_method_names = ['post', ]

    def get_success_url(self):
        return self.request.POST.get(
            'redirect_to',
            reverse('explorer:pixelset_list')
        )

    def form_valid(self, form):

        selection = list(
            set(
                get_pixel_sets_for_export(self.request.session) + [
                    str(p.id) for p in form.cleaned_data['pixel_sets']
                ]
            )
        )

        self.request.session.update({
            'export': {
                'pixelsets': selection
            }
        })

        nb_pixelsets = len(form.cleaned_data['pixel_sets'])

        messages.success(
            self.request,
            ngettext(
                '%(count)d Pixel Set has been selected for export.',
                '%(count)d Pixel Sets have been selected for export.',
                nb_pixelsets
            ) % {
                'count': nb_pixelsets,
            }
        )

        return super().form_valid(form)

    def form_invalid(self, form):

        messages.error(
            self.request,
            '\n'.join([
                f'{v[0]}' for (k, v) in form.errors.items()
            ])
        )

        return HttpResponseRedirect(self.get_success_url())


class PixelSetExportView(LoginRequiredMixin, View):

    ATTACHEMENT_FILENAME = 'pixelsets_{date_time}.zip'
    http_method_names = ['post', ]

    @staticmethod
    def get_export_archive_filename():
        return PixelSetExportView.ATTACHEMENT_FILENAME.format(
            date_time=timezone.now().strftime('%Y%m%d_%Hh%Mm%Ss')
        )

    def post(self, request, *args, **kwargs):

        selection = []
        if self.request.session.get('export', None):
            selection = self.request.session['export'].get('pixelsets', [])

        if not len(selection):
            return self.empty_selection(request)

        qs = PixelSet.objects.filter(id__in=selection)
        content = export_pixelsets(qs).getvalue()

        # Reset selection
        request.session.update({
            'export': {
                'pixelsets': []
            }
        })

        response = HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )
        return response

    def empty_selection(self, request):

        messages.error(
            request,
            _("Cannot export empty selection")
        )

        return HttpResponseRedirect(reverse('explorer:pixelset_list'))


class PixelSetDetailView(LoginRequiredMixin, FormMixin, DetailView):

    form_class = PixelSetExportPixelsForm
    http_method_names = ['get', 'post']
    model = PixelSet
    pixels_limit = 100
    template_name = 'explorer/pixelset_detail.html'

    def get_omics_units(self):

        return get_omics_units_from_session(self.request.session)

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
            request.session.update({
                'export': {
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


class PixelSetDetailValuesView(LoginRequiredMixin, DataTableView):

    def get_headers(self):

        return {'id': ('string'), 'value': ('number')}


class PixelSetDetailQualityScoresView(LoginRequiredMixin, DataTableView):

    def get_headers(self):

        return {'id': ('string'), 'quality_score': ('number')}
