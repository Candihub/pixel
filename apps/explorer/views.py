from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.core.models import PixelSet


class PixelSetListView(LoginRequiredMixin, ListView):

    model = PixelSet
    paginate_by = 10
    queryset = PixelSet.objects.all().prefetch_related(
        'analysis__experiments__omics_area',
        'pixels__omics_unit__type',
        'pixels__omics_unit__strain__species',
    )
    template_name = 'explorer/pixelset_list.html'
