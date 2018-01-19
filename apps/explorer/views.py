from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.core.models import PixelSet


class PixelSetListView(LoginRequiredMixin, ListView):

    model = PixelSet
    template_name = 'explorer/pixelset_list.html'
