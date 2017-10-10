import uuid

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel, TreeForeignKey
from tagulous import models as tgl_models


class Species(models.Model):
    """Canonical species
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        _("Name"),
        max_length=100,
    )

    reference = models.ForeignKey(
        'data.Entry',
        on_delete=models.CASCADE,
        related_name='species',
        related_query_name='species',
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Species")
        verbose_name_plural = _("Species")

    def __str__(self):
        return self.name


class Strain(models.Model):
    """Studied strains
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        _("Name"),
        max_length=100,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    species = models.ForeignKey(
        'Species',
        on_delete=models.CASCADE,
        related_name='strains',
        related_query_name='strain',
    )

    class Meta:
        verbose_name = _("Strain")
        verbose_name_plural = _("Strains")

    def __str__(self):
        return self.name


class OmicsUnitType(models.Model):
    """Omics unit type could be promoter, gene, etc.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    name = models.CharField(
        _("Name"),
        max_length=100,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Omics unit type")
        verbose_name_plural = _("Omics unit types")


class OmicsUnit(models.Model):
    """The Omics Unit could be a gene, a promoter, etc.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    reference = models.ForeignKey(
        'data.Entry',
        on_delete=models.CASCADE,
    )

    strain = models.ForeignKey(
        'Strain',
        on_delete=models.CASCADE,
        related_name='omics_units',
        related_query_name='omics_unit',
    )

    type = models.ForeignKey(
        'OmicsUnitType',
        on_delete=models.CASCADE,
        related_name='omics_units',
        related_query_name='omics_unit',
    )

    STATUS_DUBIOUS = 1
    STATUS_EXISTS = 2
    STATUS_INVALID = 3
    STATUS_VALIDATED = 4
    STATUS_CHOICES = (
        (STATUS_DUBIOUS, _("Dubious")),
        (STATUS_EXISTS, _("Exists")),
        (STATUS_INVALID, _("Invalid")),
        (STATUS_VALIDATED, _("Validated")),
    )
    status = models.PositiveSmallIntegerField(
        _("Status"),
        choices=STATUS_CHOICES,
        default=STATUS_DUBIOUS,
    )

    class Meta:
        verbose_name = _("Omics Unit")
        verbose_name_plural = _("Omics Units")

    def __str__(self):
        return self.reference


class Pixel(models.Model):
    """A pixel is the smallest measurement unit for an Omics study
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    value = models.FloatField(
        _("Value"),
        help_text=_("The pixel value")
    )

    quality_score = models.FloatField(
        _("Quality score"),
        help_text=_("Could be a p-value, confidence index, etc."),
        null=True,
        blank=True,
    )

    omics_unit = models.ForeignKey(
        'OmicsUnit',
        on_delete=models.CASCADE,
        related_name='pixels',
        related_query_name='pixel',
    )

    class Meta:
        verbose_name = _("Pixel")
        verbose_name_plural = _("Pixels")

    def __str__(self):
        return self.uuid


class Tag(tgl_models.TagModel):
    """The Pixel tag model is mostly used to add facets to experiment search.
    """

    force_lowercase = True
    tree = True


class Experiment(models.Model):
    """An experiment correspond to preliminary work on an OmicsUnit, _e.g._ a
    publication or preliminary work from a partnering laboratory.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    release_date = models.DateField(
        _("Release date"),
    )

    omics_domain = models.ForeignKey(
        'OmicsDomain',
        on_delete=models.CASCADE,
        related_name='experiments',
        related_query_name='experiment',
    )

    entries = models.ManyToManyField(
        'data.Entry',
        related_name='experiments',
        related_query_name='experiment',
    )

    tags = tgl_models.TagField(
        to=Tag,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    saved_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    class Meta:
        verbose_name = _("Experiment")
        verbose_name_plural = _("Experiments")


class Analysis(models.Model):
    """An analysis from a set of pixels
    """

    def secondary_data_upload_to(instance, filename):
        return '{0}/{1}'.format(instance.pixeler.id, instance.id)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    experiments = models.ManyToManyField(
        'Experiment',
        related_name='analyses',
        related_query_name='analysis',
    )

    pixels = models.ManyToManyField(
        'Pixel',
        related_name='analyses',
        related_query_name='analysis',
    )

    secondary_data = models.FileField(
        _("Secondary data"),
        upload_to=secondary_data_upload_to
    )

    notebook_url = models.URLField(
        _("Notebook url"),
        help_text=_("Paste an URL to your Jupiter Notebook here"),
        blank=True,
    )

    pixeler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        related_query_name='analysis',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    saved_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    class Meta:
        verbose_name = _("Analysis")
        verbose_name_plural = _("Analyses")


class OmicsDomain(MPTTModel):
    """Omics Domain (Tree)
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

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )

    class Meta:
        verbose_name = _("Omics domain")
        verbose_name_plural = _("Omics domains")

    class MPTTMeta:
        order_insertion_by = ['name']


class Pixeler(AbstractUser):
    """Pixel database user
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
