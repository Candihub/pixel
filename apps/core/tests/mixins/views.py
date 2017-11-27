from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class FooView(LoginRequiredMixin, TemplateView):

    template_name = 'base.html'
