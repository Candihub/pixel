from pathlib import PurePath
from tempfile import mkdtemp
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView, View

from .io.xlsx import generate_template


class DownloadXLSXTemplateView(LoginRequiredMixin, TemplateView):

    template_name = 'submission/download_xlsx_template.html'

    def get_context_data(self, **kwargs):
        # TODO
        # reverse the upload url
        next_step_url = '#'

        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'step': 'download',
            'next_step_url': next_step_url,
        })
        return ctx


class GenerateXLSXTemplateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        generate_template(template_path)

        response = HttpResponse(
            content_type=(
                'application/vnd'
                '.openxmlformats-officedocument'
                '.spreadsheetml'
                '.sheet'
            )
        )
        content_disposition = 'attachment; filename="{}"'.format(
            template_file_name
        )
        response['Content-Disposition'] = content_disposition

        with open(template_path, 'rb') as template:
            response.write(template.read())

        return response
