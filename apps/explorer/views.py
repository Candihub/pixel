from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from apps.core.models import PixelSet
from .forms import PixelSetFiltersForm


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

        return qs.distinct().prefetch_related(
            'analysis__experiments__omics_area',
            'analysis__experiments__tags',
            'analysis__pixeler',
            'analysis__tags',
            'pixels__omics_unit__type',
            'pixels__omics_unit__strain__species',
        )
