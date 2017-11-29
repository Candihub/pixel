from pathlib import PurePath
from tempfile import mkdtemp

from django.http import HttpResponse
from viewflow.flow.views import UpdateProcessView

from .io.xlsx import generate_template


class DownloadXLSXTemplateView(UpdateProcessView):

    template_name = 'submission/download_xlsx_template.html'

    def get_context_data(self, **kwargs):

        process = self.get_object()

        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'task_list': process.task_set.all().order_by('created'),
        })

        return ctx

    def post(self, request, *args, **kwargs):

        template_file_name = 'meta.xlsx'
        template_path = PurePath(mkdtemp(), template_file_name)
        checksum, version = generate_template(filename=template_path)

        process = self.get_object()
        process.downloaded = True
        process.template_checksum = checksum
        process.template_version = version
        process.save()
        self.activation_done()

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


class UploadArchiveView(UpdateProcessView):

    template_name = 'submission/upload_archive.html'
    fields = ['archive', ]

    def form_valid(self, form):

        process = form.save(commit=False)
        process.uploaded = True
        process.save()

        return super().form_valid(form)


class ArchiveValidationView(UpdateProcessView):

    template_name = 'submission/validation.html'
    fields = ['validated', ]
