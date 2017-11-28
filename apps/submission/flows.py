from viewflow import flow
from viewflow.base import this, Flow
from viewflow.flow.views import CreateProcessView

from .models import SubmissionProcess
from .views import DownloadXLSXTemplateView, UploadArchiveView


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

    check_download = flow.If(
        lambda activation: activation.process.downloaded
    ).Then(
        this.upload
    ).Else(
        this.download
    )

    upload = flow.View(
        UploadArchiveView,
    ).Assign(
        this.start.owner
    ).Next(
        this.check_upload
    )

    check_upload = flow.If(
        lambda activation: activation.process.uploaded
    ).Then(
        this.end
    ).Else(
        this.upload
    )

    end = flow.End()
