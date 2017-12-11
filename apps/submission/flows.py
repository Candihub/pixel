from pathlib import Path

from django.conf import settings
from viewflow import flow
from viewflow.activation import Context
from viewflow.base import this, Flow
from viewflow.flow.views import CreateProcessView
from viewflow.nodes.handler import HandlerActivation

from apps.submission.io.archive import PixelArchive
from .models import SubmissionProcess
from . import views


class NotPropagatedExceptionHandlerActivation(HandlerActivation):

    def perform(self):

        with Context(propagate_exception=False):
            super().perform()


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
        views.DownloadXLSXTemplateView,
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
        views.UploadArchiveView,
    ).Assign(
        this.start.owner
    ).Next(
        this.check_upload
    )

    check_upload = flow.If(
        lambda activation: activation.process.uploaded
    ).Then(
        this.meta
    ).Else(
        this.upload
    )

    meta = flow.Handler(
        this.parse_meta,
        activation_class=NotPropagatedExceptionHandlerActivation,
    ).Next(
        this.check_meta
    )

    check_meta = flow.If(
        lambda activation: activation.process.meta is not None
    ).Then(
        this.validation
    ).Else(
        this.upload
    )

    validation = flow.View(
        views.ArchiveValidationView,
    ).Assign(
        this.start.owner
    ).Next(
        this.check_validation
    )

    check_validation = flow.If(
        lambda activation: activation.process.validated
    ).Then(
        this.end
    ).Else(
        this.validation
    )

    end = flow.End()

    def parse_meta(self, activation):

        archive_path = Path(
            settings.MEDIA_ROOT
        ) / Path(
            activation.process.archive.name
        )
        archive = PixelArchive(archive_path)
        archive.parse_meta(serialized=True)
        activation.process.meta = archive.meta
        activation.process.save()
