from django.contrib import admin
from . import models


class AnalysisAdmin(admin.ModelAdmin):
    pass


class ExperimentAdmin(admin.ModelAdmin):
    pass


class OmicsAreaAdmin(admin.ModelAdmin):
    pass


class OmicsUnitAdmin(admin.ModelAdmin):
    pass


class OmicsUnitTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']
    list_display = (
        'name', 'description'
    )


class PixelAdmin(admin.ModelAdmin):
    pass


class SpeciesAdmin(admin.ModelAdmin):
    model = models.Species
    list_display = (
        'name', 'description', 'reference'
    )
    ordering = ['name']


class StrainAdmin(admin.ModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    model = models.Tag


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
