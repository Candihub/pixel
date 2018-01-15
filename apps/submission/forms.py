from django import forms
from django.utils.translation import ugettext as _

from apps.core.models import Tag
from .models import SubmissionProcess


class SubmissionTagsForm(forms.ModelForm):

    def _get_tags():
        return [(t.name, t.name) for t in Tag.objects.all()]

    experiment_tags = forms.ChoiceField(
        label=_("Select one or more tags"),
        choices=_get_tags,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    analysis_tags = forms.ChoiceField(
        label=_("Select one or more tags"),
        choices=_get_tags,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    new_experiment_tags = forms.CharField(
        label=_("and/or add new tags"),
        help_text=_(
            "Type coma-separated tags. Tree level separator is the slash. "
            "Example: 'NGS, single-cell/RNA' will add the 'NGS' tag and the "
            "'RNA' tag that has 'single-cell' as parent tag in the tag tree."
        ),
        widget=forms.TextInput(
            attrs={
                'placeholder': _("NGS, single-cell/RNA")
            },
        ),
        required=False,
    )

    new_analysis_tags = forms.CharField(
        label=_("and/or add new tags"),
        help_text=_(
            "Type coma-separated tags. Tree level separator is the slash. "
            "Example: 'NGS, single-cell/RNA' will add the 'NGS' tag and the "
            "'RNA' tag that has 'single-cell' as parent tag in the tag tree."
        ),
        widget=forms.TextInput(
            attrs={
                'placeholder': _("NGS, single-cell/RNA")
            },
        ),
        required=False,
    )

    class Meta:
        model = SubmissionProcess
        fields = ['tags', ]
        widgets = {
            'tags': forms.HiddenInput,
        }
