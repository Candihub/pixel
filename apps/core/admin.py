from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import models


class UUIDModelAdminMixin(object):

    def get_short_uuid(self, obj):
        return str(obj)
    get_short_uuid.short_description = 'ID'


@admin.register(models.Analysis)
class AnalysisAdmin(UUIDModelAdminMixin, admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'description', 'pixeler',
        'created_at', 'saved_at',
    )
    list_filter = ('created_at', 'saved_at', 'tags', 'experiments__omics_area')


@admin.register(models.Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'created_at', 'released_at', 'saved_at',
    )
    list_filter = ('tags', 'entries')


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
    get_species.short_description = 'Species'

    def get_reference_identifier(self, obj):
        return obj.reference.identifier
    get_reference_identifier.short_description = 'Entry identifier'


@admin.register(models.OmicsUnitType)
class OmicsUnitTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'description'
    )


@admin.register(models.Pixel)
class PixelAdmin(admin.ModelAdmin):
    list_display = (
        'get_short_uuid', 'value', 'quality_score', 'omics_unit',
        'get_analysis_description',
    )
    list_filter = (
        'omics_unit__type', 'analysis__experiments__omics_area'
    )

    def get_analysis_description(self, obj):
        return obj.analysis.description
    get_analysis_description.short_description = 'Analysis'


@admin.register(models.Pixeler)
class PixelerAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name',
        'last_name', 'email', 'last_login',
    )
    list_filter = ('is_superuser', 'is_active', 'is_staff')


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

    def get_species(self, obj):
        return (obj.species.name)
    get_species.short_description = 'Species'

    def get_entry_identifier(self, obj):
        if obj.reference is None:
            return '-'
            
        return obj.reference.identifier
    list_filter = ('species__name',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name', 'label', 'level', 'count', 'parent'
    )
