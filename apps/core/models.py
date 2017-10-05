import uuid

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel, TreeForeignKey


class PublicDatabase(models.Model):
    """Public Database from where reference identifiers are extracted
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

    url = models.URLField(
        _("URL"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Public Database")
        verbose_name_plural = _("Public Databases")

    def __str__(self):
        return self.name


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

    reference_identifier = models.CharField(
        _("Reference Identifier"),
        max_length=100,
        blank=True,
    )

    reference_database = models.ForeignKey(
        'PublicDatabase',
        on_delete=models.CASCADE,
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

    reference_identifier = models.CharField(
        _("Reference Identifier"),
        max_length=100,
        blank=True,
    )

    custom_identifier = models.CharField(
        _("Custom Identifier"),
        max_length=100,
        blank=True,
    )

    reference_database = models.ForeignKey(
        'PublicDatabase',
        on_delete=models.CASCADE,
    )

    strain = models.ForeignKey(
        'Strain',
        on_delete=models.CASCADE,
    )

    type = models.ForeignKey(
        'OmicsUnitType',
        on_delete=models.CASCADE,
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
        return self.original_identifier or self.custom_identifier

    def clean(self):
        """An OmicsUnit should have at least an original or a custom identifier
        """
        if not self.original_identifier and not self.custom_identifier:
            raise ValidationError(
                _("You need to provide an identifier (custom or original)")
            )


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
    )

    class Meta:
        verbose_name = _("Pixel")
        verbose_name_plural = _("Pixels")

    def __str__(self):
        return self.uuid


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

    primary_data_url = models.URLField(
        _("Primary data url"),
    )

    release_date = models.DateField(
        _("Release date"),
    )

    omics_domain = models.ForeignKey(
        'OmicsDomain',
        on_delete=models.CASCADE,
    )

    omics_units = models.ManyToManyField(
        'OmicsUnit',
        related_name='experiments',
        related_query_name='experiment',
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

    pixeler = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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


class DataSource(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    TYPE_DB = 1
    TYPE_PAPER = 2
    TYPE_PARTNER = 3
    TYPE_CHOICES = (
        (TYPE_DB, _("Public database")),
        (TYPE_PAPER, _("Scientific publication")),
        (TYPE_PARTNER, _("Partnering laboratory")),
    )
    type = models.PositiveSmallIntegerField(
        _("Source type"),
        choices=TYPE_CHOICES,
        default=TYPE_DB,
    )

    reference_identifier = models.CharField(
        _("Reference Identifier"),
        max_length=100,
        blank=True,
    )

    description = models.TextField(
        _("Description"),
        blank=True,
    )

    primary_data_url = models.URLField(
        _("Primary data url"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Data source")
        verbose_name_plural = _("Data sources")
