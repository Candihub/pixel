from pathlib import PurePath
from tempfile import mkdtemp

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View

from .io.xlsx import generate_template


class DownloadXLSXTemplateView(LoginRequiredMixin, TemplateView):

    template_name = 'submission/download_xlsx_template.html'

    def get(self, request, *args, **kwargs):
        check = True if request.GET.get('check') else False
        context = self.get_context_data(check=check, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, check=False, **kwargs):
        # TODO
        # reverse the upload url
        next_step_url = '#'

        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'step': 'download',
            'next_step_url': next_step_url,
            'check': check,
        })

        meta = self.request.session.get('template')
        if meta:
            ctx.update({
                'version': meta.get('version'),
                'checksum': meta.get('checksum'),
            })

        if check and not meta:
            messages.warning(
                self.request,
                _(
                    "Download the meta.xlsx template first. "
                    "Then you will be able to display its checksum."
                )
            )

        return ctx


class GenerateXLSXTemplateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        checksum, version = generate_template(filename=template_path)

        # Save file checksum in the session
        request.session['template'] = {
            'checksum': checksum,
            'version': version,
        }

        response = HttpResponse(
            content_type=(
                'application/vnd'
                '.openxmlformats-officedocument'
                '.spreadsheetml'
                '.sheet'
            )
        )
        content_disposition = 'attachment; filename="{}"'.format(
            '{}-{}.xlsx'.format(
                template_path.stem,
                version[:8]
            )
        )
        response['Content-Disposition'] = content_disposition

        with open(template_path, 'rb') as template:
            response.write(template.read())

        return response
