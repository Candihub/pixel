import uuid
import mptt

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from tagulous import models as tgl_models

from .mixins import UUIDModelMixin


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
        unique=True,
    )

    reference = models.ForeignKey(
        'data.Entry',
        on_delete=models.CASCADE,
        related_name='species',
        related_query_name='species',
        blank=True,
        null=True,
    )

    repository = models.ForeignKey(
        'data.Repository',
        on_delete=models.CASCADE,
        related_name='species',
        related_query_name='species',
        blank=True,
        null=True,
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

    reference = models.ForeignKey(
        'data.Entry',
        on_delete=models.CASCADE,
        related_name='strains',
        related_query_name='strain',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Strain")
        verbose_name_plural = _("Strains")
        unique_together = (
            ('name', 'species'),
        )

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
        unique=True,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Omics unit type")
        verbose_name_plural = _("Omics unit types")

    def __str__(self):
        return self.name


class OmicsUnit(UUIDModelMixin, models.Model):
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
        unique_together = (
            ('reference', 'strain', 'type')
        )

    def __str__(self):
        return '{} ({}/{}/{})'.format(
                self.get_short_uuid(),
                self.type,
                self.strain,
                self.strain.species.name
                )


class PixelSet(UUIDModelMixin, models.Model):
    """A pixelset is a collection of pixels for an analysis
    """

    def pixelset_upload_to(instance, filename):
        return '{}/{}/pixelsets/{}'.format(
            instance.analysis.pixeler.id,
            instance.analysis.id,
            filename
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    pixels_file = models.FileField(
        _("Pixels file"),
        upload_to=pixelset_upload_to,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    analysis = models.ForeignKey(
        'Analysis',
        on_delete=models.CASCADE,
        related_name='pixelsets',
        related_query_name='pixelset',
    )


class Pixel(UUIDModelMixin, models.Model):
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

    pixel_set = models.ForeignKey(
        'PixelSet',
        on_delete=models.CASCADE,
        related_name='pixels',
        related_query_name='pixel',
    )

    class Meta:
        verbose_name = _("Pixel")
        verbose_name_plural = _("Pixels")


class Tag(tgl_models.TagTreeModel):
    """The Pixel tag model is mostly used to add facets to experiment search.
    """

    class TagMeta:
        force_lowercase = True


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

    omics_area = mptt.fields.TreeForeignKey(
        'OmicsArea',
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

    completed_at = models.DateField(
        _("Completion date"),
    )

    released_at = models.DateField(
        _("Release date"),
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


class Analysis(UUIDModelMixin, models.Model):
    """An analysis from a set of pixels
    """

    def secondary_data_upload_to(instance, filename):
        return '{0}/{1}/secondary_data'.format(
            instance.pixeler.id, instance.id
        )

    def notebook_upload_to(instance, filename):
        return '{0}/{1}/notebook'.format(
            instance.pixeler.id, instance.id
        )

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

    secondary_data = models.FileField(
        _("Secondary data"),
        upload_to=secondary_data_upload_to,
    )

    notebook = models.FileField(
        _("Notebook"),
        help_text=_(
            "Upload your Jupiter Notebook or any other document helping to "
            "understand your analysis"
        ),
        blank=True,
        upload_to=notebook_upload_to,
    )

    pixeler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        related_query_name='analysis',
    )

    tags = tgl_models.TagField(
        to=Tag,
    )

    completed_at = models.DateField(
        _("Completion date"),
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


class OmicsArea(MPTTModel):
    """Omics Area (Tree)
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
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )

    class Meta:
        verbose_name = _("Omics area")
        verbose_name_plural = _("Omics areas")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return str(self.name)


class Pixeler(AbstractUser):
    """Pixel database user
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        verbose_name = _("Pixeler")
        verbose_name_plural = _("Pixelers")
