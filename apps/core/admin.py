from django.contrib import admin
from . import models


class AnalysisAdmin(admin.ModelAdmin):
    model = models.Analysis
    list_display = (
        'description', 'pixeler', 'created_at', 'saved_at',
        'notebook', 'secondary_data'
    )
    list_filter = ('created_at', 'saved_at')


class ExperimentAdmin(admin.ModelAdmin):
    model = models.Analysis
    list_display = (
        'description', 'created_at', 'released_at', 'saved_at',
        'get_omics_area', 'get_tags', 'get_entries'
    )

    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_entries(self, obj):
        return "\n".join([e.identifier for e in obj.entries.all()])
    get_entries.short_description = 'Entries'

    def get_omics_area(self, obj):
        return (obj.omics_area.name)
    get_omics_area.short_description = 'Omics area'


class OmicsAreaAdmin(admin.ModelAdmin):
    model = models.OmicsArea
    list_display = (
        'name', 'description', 'level', 'parent'
    )


class OmicsUnitAdmin(admin.ModelAdmin):
    model = models.OmicsUnit
    list_display = (
        'entry_identifier', 'strain', 'get_species', 'type', 'status'
    )

    def get_species(self, obj):
        return (obj.strain.species.name)

    def entry_identifier(self, obj):
        return (obj.reference.identifier)

    entry_identifier.short_description = 'Entry identifier'
    list_filter = ['status']


class OmicsUnitTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    list_display = (
        'name', 'description'
    )


class PixelAdmin(admin.ModelAdmin):
    model = models.Pixel
    list_display = (
        'get_analysis', 'get_species', 'get_strain',  'quality_score'
    )

    def get_analysis(self, obj):
        return (obj.analysis.description)
    get_analysis.short_description = 'Analysis'

    def get_species(self, obj):
        return (obj.omics_unit.get_species())
    get_species.short_description = 'Species'

    def get_strain(self, obj):
        return (obj.omics_unit.get_strain())
    get_strain.short_description = 'Strain'


class SpeciesAdmin(admin.ModelAdmin):
    search_fields = ['name']
    model = models.Species
    list_display = (
        'name', 'description', 'reference', 'repository'
    )
    ordering = ['name']


class StrainAdmin(admin.ModelAdmin):
    search_fields = ['name']
    model = models.Strain
    list_display = (
        'name', 'description', 'get_species', 'entry_identifier'
    )

    def get_species(self, obj):
        return (obj.species.name)
    get_species.short_description = 'Species'

    def entry_identifier(self, obj):
        if obj.reference is not None:
            return (obj.reference.identifier)
        else:
            return ("-")
    list_filter = ('species__name',)


class TagAdmin(admin.ModelAdmin):
    model = models.Tag
    search_fields = ['name']
    list_display = (
        'name', 'label', 'level', 'count', 'parent'
    )


class PixelerAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name',
                    'last_name', 'email', 'last_login'
                    )
    list_filter = ('is_superuser', 'is_active', 'is_staff')


admin.site.register(models.Analysis, AnalysisAdmin)
admin.site.register(models.Experiment, ExperimentAdmin)
admin.site.register(models.OmicsArea, OmicsAreaAdmin)
admin.site.register(models.OmicsUnit, OmicsUnitAdmin)
admin.site.register(models.OmicsUnitType, OmicsUnitTypeAdmin)
admin.site.register(models.Pixel, PixelAdmin)
admin.site.register(models.Pixeler, PixelerAdmin)
admin.site.register(models.Species, SpeciesAdmin)
admin.site.register(models.Strain, StrainAdmin)
admin.site.register(models.Tag, TagAdmin)
