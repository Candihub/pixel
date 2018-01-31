import re

from django import forms
from django.utils.translation import ugettext as _
from mptt.forms import TreeNodeMultipleChoiceField

from apps.core import models


def str_to_set(input):
    """Returns a set of strings by splitting the given `input` string on space,
    comma or new line. It eliminates duplicates and strips each string.
    """
    return set(
        # Remove (filter) empty string values
        filter(
            None,
            [part.strip() for part in re.split('\s*,\s*|\s+|\n', input)]
        )
    )


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

    def clean_search(self):
        return self.cleaned_data['search'].strip()


class PixelSetExportForm(forms.Form):

    pixel_sets = forms.ModelMultipleChoiceField(
        queryset=models.PixelSet.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={
            'required': _('You must select at least one Pixel Set.'),
        },
    )


class PixelSetSelectForm(PixelSetExportForm):
    pass


class SessionPixelSetSelectForm(forms.Form):

    pixel_set = forms.ChoiceField(
        choices=[],
        error_messages={
            'required': _('You must pick on pixel set from stored selection.'),
        },
    )

    def __init__(self, session_pixel_sets, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pixel_set'].choices = (
            (p, p) for p in session_pixel_sets
        )


class PixelSetExportPixelsForm(forms.Form):

    omics_units = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': _('CAGL0F02695g, CAGL0D06336g, CAGL0G06666g'),
                'rows': 15,
            }
        ),
        help_text=_(
            'Type omics units separated by a comma, a carriage return or a'
            ' space'
        ),
        required=False,
    )

    def clean_omics_units(self):
        return list(str_to_set(self.cleaned_data['omics_units']))
