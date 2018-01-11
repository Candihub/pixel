from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext as _
from viewflow.activation import STATUS
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
        max_length=255,
    )

    template_checksum = models.CharField(
        _("Template checksum"),
        help_text=_("Downloaded XLSX template checksum"),
        max_length=64,
        blank=True,
    )

    template_version = models.CharField(
        _("Template version"),
        help_text=_("Downloaded XLSX template version"),
        max_length=64,
        blank=True,
    )

    meta = JSONField(
        _("Meta"),
        encoder=DjangoJSONEncoder,
        help_text=_("Submitted archive meta.xlsx parsed data"),
        null=True,
        blank=True,
    )

    downloaded = models.BooleanField(default=False)

    uploaded = models.BooleanField(default=False)

    validated = models.BooleanField(
        _("Is validated?"),
        help_text=_("Check this to validate parsed metadata"),
        default=False
    )

    imported = models.BooleanField(default=False)

    @property
    def has_failed(self):
        """Check if process has failed tasks"""

        if self.task_set.filter(status=STATUS.ERROR).count() > 0:
            return True
        return False

    @property
    def is_done(self):
        """Check if the process is done"""

        if self.status == STATUS.DONE:
            return True
        return False
