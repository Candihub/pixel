from pathlib import PurePath
from tempfile import mkdtemp

from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from viewflow.flow.views import UpdateProcessView

from .io.xlsx import generate_template


class DownloadXLSXTemplateView(UpdateProcessView):

    template_name = 'submission/download_xlsx_template.html'

    def get_context_data(self, **kwargs):

        check = True if self.request.GET.get('check') else False
        process = self.get_object()

        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'task_list': process.task_set.all().order_by('created'),
            'step': 'download',
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

    def post(self, request, *args, **kwargs):

        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        checksum, version = generate_template(filename=template_path)

        # Update process
        process = self.get_object()
        process.downloaded = True
        process.save()
        self.activation_done()

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
