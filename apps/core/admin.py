from django.contrib import admin
from .models import (
    Analysis, Experiment, OmicsArea, OmicsUnit, OmicsUnitType, Pixel, Pixeler,
    Species, Strain, Tag
)

admin.site.register(Species)
admin.site.register(Strain)
admin.site.register(OmicsUnitType)
admin.site.register(OmicsUnit)
admin.site.register(Pixel)
admin.site.register(Tag)
admin.site.register(Experiment)
admin.site.register(Analysis)
admin.site.register(OmicsArea)
admin.site.register(Pixeler)
