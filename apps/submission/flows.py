from viewflow import flow
from viewflow.base import this, Flow
from viewflow.flow.views import CreateProcessView

from .models import SubmissionProcess
from .views import DownloadXLSXTemplateView


class SubmissionFlow(Flow):

    process_class = SubmissionProcess

    start = flow.Start(
        CreateProcessView,
        fields=['label']
    ).Permission(
        auto_create=True
    ).Next(
        this.download
    )

    download = flow.View(
        DownloadXLSXTemplateView,
    ).Assign(
        this.start.owner
    ).Next(
        this.check_download
    )

    check_download = (
        flow.If(lambda activation: activation.process.downloaded)
        .Then(this.end)
        .Else(this.end)
    )

    end = flow.End()

    def send_hello_world_request(self, activation):
        print(activation.process.label)
