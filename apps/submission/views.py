from pathlib import PurePath
from tempfile import mkdtemp

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin
from viewflow.models import Task
from viewflow.flow.views import UpdateProcessView

from .io.xlsx import generate_template
from .forms import SubmissionTagsForm
from .models import SubmissionProcess
from .utils import is_hidden_task


class NextTaskRedirectView(SingleObjectMixin,
                           RedirectView):

    model = SubmissionProcess
    pk_url_kwarg = 'process_pk'

    def get_process_tasks(self, process, user):

        task_class = process.flow_class.task_class
        return task_class._default_manager.user_queue(user).filter(
            process=process
        )

    def get_redirect_url(self, *args, **kwargs):

        namespace = self.request.resolver_match.namespace
        process = self.get_object()
        task_pk = kwargs.get('task_pk')
        user_tasks = self.get_process_tasks(process, self.request.user)

        default_url = reverse(
            '{}:detail'.format(namespace),
            kwargs={'process_pk': process.pk}
        )

        if not user_tasks.exists():
            return default_url

        try:
            task = user_tasks.get(pk=task_pk)
        except Task.DoesNotExist:
            return default_url

        def get_next_task(task):
            if task.leading.count():
                next_task = task.leading.get()
                if is_hidden_task(str(next_task.flow_task).lower()):
                    return get_next_task(next_task)
                return next_task
            return task

        next_task = get_next_task(task)
        return next_task.flow_task.get_task_url(
            next_task,
            url_type='guess',
            user=self.request.user,
            namespace=namespace
        )


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


class TagsView(UpdateProcessView):

    template_name = 'submission/tags.html'
    form_class = SubmissionTagsForm
