from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from mptt.admin import MPTTModelAdmin

from . import models


class UUIDModelAdminMixin(object):

    def get_short_uuid(self, obj):
        return str(obj)
    get_short_uuid.short_description = 'ID'


class TagsModelAdminMixin(object):

    def get_tags(self, obj):
        return str(obj.tags)
    get_tags.short_description = _("Tags")


@admin.register(models.Analysis)
class AnalysisAdmin(UUIDModelAdminMixin,
                    TagsModelAdminMixin,
                    admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'description', 'pixeler', 'get_tags',
        'created_at', 'saved_at',
    )
    list_filter = ('experiments__omics_area', 'tags', 'created_at', 'saved_at')


@admin.register(models.Experiment)
class ExperimentAdmin(UUIDModelAdminMixin,
                      TagsModelAdminMixin,
                      admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'description', 'omics_area', 'get_tags',
        'completed_at', 'released_at',
    )
    list_filter = ('omics_area', 'tags', 'created_at', 'saved_at')
    raw_id_fields = ('entries', )


@admin.register(models.OmicsArea)
class OmicsAreaAdmin(MPTTModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'description', 'level'
    )


@admin.register(models.OmicsUnit)
class OmicsUnitAdmin(UUIDModelAdminMixin, admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'get_reference_identifier',
        'strain', 'get_species', 'type', 'status'
    )
    list_filter = ['status', 'type', 'strain__species__name', ]

    def get_species(self, obj):
        return obj.strain.species.name
    get_species.short_description = _("Species")

    def get_reference_identifier(self, obj):
        return obj.reference.identifier
    get_reference_identifier.short_description = _("Entry identifier")


@admin.register(models.OmicsUnitType)
class OmicsUnitTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'description'
    )


@admin.register(models.PixelSet)
class PixelSetAdmin(admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'description', 'analysis'
    )
    list_filter = (
        'analysis__experiments__omics_area',
    )


@admin.register(models.Pixel)
class PixelAdmin(admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'value', 'quality_score', 'omics_unit',
        'get_analysis_description',
    )
    list_filter = (
        'omics_unit__type', 'pixel_set__analysis__experiments__omics_area'
    )

    def get_analysis_description(self, obj):
        return obj.pixel_set.analysis.description
    get_analysis_description.short_description = _("Analysis")


@admin.register(models.Pixeler)
class PixelerAdmin(UserAdmin):
    pass


@admin.register(models.Species)
class SpeciesAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'description', 'reference', 'repository'
    )


@admin.register(models.Strain)
class StrainAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'description', 'get_species', 'get_entry_identifier'
    )
    list_filter = ('species__name',)

    def get_species(self, obj):
        return (obj.species.name)
    get_species.short_description = _("Species")

    def get_entry_identifier(self, obj):
        if obj.reference is None:
            return '-'
        return obj.reference.identifier
    get_entry_identifier.short_description = _("Reference")


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'label', 'level', 'count', 'parent'
    )
