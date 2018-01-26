from django import forms
from django.utils.translation import ugettext as _
from mptt.forms import TreeNodeMultipleChoiceField

from apps.core import models


class PixelSetFiltersForm(forms.Form):

    species = forms.ModelMultipleChoiceField(
        label=_("Species"),
        queryset=models.Species.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    omics_unit_types = forms.ModelMultipleChoiceField(
        label=_("Omics Unit Types"),
        queryset=models.OmicsUnitType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    omics_areas = TreeNodeMultipleChoiceField(
        label=_("Omics Areas"),
        queryset=models.OmicsArea.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        level_indicator='—',
        required=False,
    )

    tags = forms.ModelMultipleChoiceField(
        label=_("Tags"),
        queryset=models.Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    search = forms.CharField(
        label=_("Search"),
        widget=forms.TextInput(
            attrs={
                'placeholder': _("CAGL0A02321g"),
            }
        ),
        help_text=_(
            "Type a gene name or a key word, e.g. CAGL0A02321g or LIMMA"
        ),
        required=False,
    )


class PixelSetExportForm(forms.Form):

    pixel_sets = forms.ModelMultipleChoiceField(
        queryset=models.PixelSet.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={
            'required': _('You must select at least one Pixel Set.'),
        },
    )
