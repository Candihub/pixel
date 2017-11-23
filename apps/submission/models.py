from django.db import models
from django.utils.translation import ugettext as _
from viewflow.models import Process


class SubmissionProcess(Process):

    def archive_upload_to(instance, filename):
        return '{}/submissions/{}/{}'.format(
            instance.created_by.id,
            instance.id,
            filename
        )

    label = models.CharField(
        _("Label"),
        max_length=150,
        help_text=_(
            "Give this new submission a label so that you'll recover it easily"
        )
    )

    archive = models.FileField(
        _("Pixels submitted archive"),
        upload_to=archive_upload_to,
    )

    downloaded = models.BooleanField(default=False)

    uploaded = models.BooleanField(default=False)

    validated = models.BooleanField(default=False)

    imported = models.BooleanField(default=False)
