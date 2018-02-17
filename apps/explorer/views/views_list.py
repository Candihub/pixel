from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _, ngettext
from django.views.generic import (
    FormView, ListView, RedirectView, View
)
from django.views.generic.edit import FormMixin

from apps.core.models import OmicsArea, PixelSet, Tag

from ..forms import (
    PixelSetFiltersForm, PixelSetExportForm,
    PixelSetSelectForm, SessionPixelSetSelectForm
)
from ..utils import export_pixelsets

from .helpers import (
    get_selected_pixel_sets_from_session, set_selected_pixel_sets_to_session
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

        selected_pixelsets = get_selected_pixel_sets_from_session(
            self.request.session
        )
        if len(selected_pixelsets):
            selected_pixelsets = PixelSet.objects.filter(
                id__in=selected_pixelsets
            )

        context = super().get_context_data(**kwargs)
        context.update({
            'export_form': PixelSetExportForm(),
            'select_form': PixelSetSelectForm(),
            'selected_pixelsets': selected_pixelsets,
        })
        return context


class PixelSetClearView(LoginRequiredMixin, RedirectView):

    http_method_names = ['post', ]

    def get_redirect_url(self, *args, **kwargs):
        return self.request.POST.get(
            'redirect_to',
            reverse('explorer:pixelset_list')
        )

    def post(self, request, *args, **kwargs):

        set_selected_pixel_sets_to_session(request.session, [])

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

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.request.session
        )

        return form_class(session_pixel_sets, **self.get_form_kwargs())

    def form_valid(self, form):

        session_pixel_sets = get_selected_pixel_sets_from_session(
            self.request.session
        )
        pixel_set = form.cleaned_data['pixel_set']
        session_pixel_sets.remove(pixel_set)

        set_selected_pixel_sets_to_session(
            self.request.session,
            pixel_sets=session_pixel_sets
        )

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
                get_selected_pixel_sets_from_session(self.request.session) + [
                    str(p.id) for p in form.cleaned_data['pixel_sets']
                ]
            )
        )

        set_selected_pixel_sets_to_session(
            self.request.session,
            pixel_sets=selection
        )

        nb_pixelsets = len(form.cleaned_data['pixel_sets'])

        messages.success(
            self.request,
            ngettext(
                '%(count)d Pixel Set has been added to your selection.',
                '%(count)d Pixel Sets have been added to your selection.',
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

        selection = get_selected_pixel_sets_from_session(self.request.session)

        if not len(selection):
            return self.empty_selection(request)

        qs = PixelSet.objects.filter(id__in=selection)
        content = export_pixelsets(qs).getvalue()

        response = HttpResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            self.get_export_archive_filename()
        )
        return response

    def empty_selection(self, request):

        messages.error(
            request,
            _("Cannot export an empty selection.")
        )

        return HttpResponseRedirect(reverse('explorer:pixelset_list'))
