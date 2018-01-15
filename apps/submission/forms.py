from django import forms
from django.utils.translation import ugettext as _

from apps.core.models import Tag
from .models import SubmissionProcess


class SubmissionTagsForm(forms.ModelForm):

    def _get_existing_tags():
        return [(t.name, t.name) for t in Tag.objects.all()]

    experiment_tags = forms.MultipleChoiceField(
        label=_("Select one or more tags"),
        choices=_get_existing_tags,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    analysis_tags = forms.MultipleChoiceField(
        label=_("Select one or more tags"),
        choices=_get_existing_tags,
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

    @staticmethod
    def _clean_tags(tags):
        """Clean input tags: sorted, stripped, lowercase and unique"""

        return ','.join(
            sorted(set(t.lower().strip() for t in tags.split(',')))
        )

    def _set_tags(self):
        """Set process tags"""

        if not hasattr(self, 'cleaned_data'):
            return

        analysis_tags = self._clean_tags(
            ','.join((
                ','.join(self.cleaned_data['analysis_tags']),
                self.cleaned_data['new_analysis_tags'],
            ))
        )

        experiment_tags = self._clean_tags(
            ','.join((
                ','.join(self.cleaned_data['experiment_tags']),
                self.cleaned_data['new_experiment_tags'],
            ))
        )

        self.instance.tags = self.cleaned_data['tags'] = {
            'analysis': analysis_tags,
            'experiment': experiment_tags,
        }

    def clean_new_experiment_tags(self):
        return self._clean_tags(self.cleaned_data['new_experiment_tags'])

    def clean_new_analysis_tags(self):
        return self._clean_tags(self.cleaned_data['new_analysis_tags'])

    def save(self, **kwargs):
        """Set tags before saving"""

        self._set_tags()

        return super().save(**kwargs)
