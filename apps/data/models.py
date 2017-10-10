import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _


class Repository(models.Model):
    """A repository is a provider from where reference data can be fetched.
    It can be a public database or a private source of data.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        _("Name"),
        max_length=100,
        unique=True,
    )

    url = models.URLField(
        _("URL"),
        help_text=_("Repository root URL"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Repository")
        verbose_name_plural = _("Repositories")

    def __str__(self):
        return self.name


class Entry(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    identifier = models.CharField(
        _("Identifier"),
        max_length=100,
        help_text=_("The repository identifier (e.g. PMID for PubMed)"),
        blank=True,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    url = models.URLField(
        _("URL"),
        help_text=_("Paste here the URL pointing to the data source"),
        blank=True,
    )

    repository = models.ForeignKey(
        'Repository',
        on_delete=models.CASCADE,
        related_name='entries',
        related_query_name='entry',
    )

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")
        unique_together = (
            ('identifier', 'repository'),
            ('url', 'repository'),
        )

    def clean(self):
        """An Entry should have at least an identifier or an url
        """
        if not self.identifier and not self.url:
            raise ValidationError(
                _("You need to provide an identifier or an url for an Entry")
            )
