from django import forms
from django.utils.translation import ugettext as _

from apps.core import models


class PixelSetFiltersForm(forms.Form):

    def get_species():
        return ((s.id, s.name) for s in models.Species.objects.all())

    def get_omics_unit_types():
        return ((o.id, o.name) for o in models.OmicsUnitType.objects.all())

    def get_omics_areas():
        return ((o.id, o.name) for o in models.OmicsArea.objects.all())

    def get_tags():
        return ((t.id, t.name) for t in models.Tag.objects.all())

    species = forms.MultipleChoiceField(
        label=_("Species"),
        choices=get_species(),
        required=False,
    )

    omics_unit_types = forms.MultipleChoiceField(
        label=_("Omics Unit Types"),
        choices=get_omics_unit_types(),
        required=False,
    )

    omics_areas = forms.MultipleChoiceField(
        label=_("Omics Areas"),
        choices=get_omics_areas(),
        required=False,
    )

    tags = forms.MultipleChoiceField(
        label=_("Tags"),
        choices=get_tags(),
        required=False,
    )
