from django import forms
from django.test import TestCase
from django.urls import reverse

from apps.core.factories import PIXELER_PASSWORD, PixelerFactory
from apps.core.models import Tag
from ..forms import SubmissionTagsForm
from ..models import SubmissionProcess


class SubmissionTagsFormTestCase(TestCase):

    def setUp(self):

        # Create submission process
        user = PixelerFactory(
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client.login(
            username=user.username,
            password=PIXELER_PASSWORD,
        )
        self.client.post(
            reverse('submission:start'),
            data={
                'label': 'Candida datasest 0001',
                '_viewflow_activation-started': '2000-01-01',
            },
            follow=True,
        )
        self.process = SubmissionProcess.objects.get()

        # Create tags
        tags = (
            'complex/molecule/atom',
            'omics/rna',
            'omics/dna',
            'omics/protein',
            'msms',
        )
        for tag in tags:
            Tag.objects.create(name=tag)

    def test__get_existing_tags(self):

        expected = [
            ('complex', 'complex'),
            ('complex/molecule', 'complex/molecule'),
            ('complex/molecule/atom', 'complex/molecule/atom'),
            ('msms', 'msms'),
            ('omics', 'omics'),
            ('omics/dna', 'omics/dna'),
            ('omics/protein', 'omics/protein'),
            ('omics/rna', 'omics/rna'),
        ]
        self.assertEqual(SubmissionTagsForm._get_existing_tags(), expected)

    def test__clean_tags(self):

        tags = ''
        expected = ''
        self.assertEqual(SubmissionTagsForm._clean_tags(tags), expected)

        tags = ' OMICS/protein, omics, Omics , complex, complex/Molecule  '
        expected = 'complex,complex/molecule,omics,omics/protein'
        self.assertEqual(SubmissionTagsForm._clean_tags(tags), expected)

        # Minimal tag length is 2
        tags = 'complex/modecule,R'
        with self.assertRaises(forms.ValidationError) as e:
            SubmissionTagsForm._clean_tags(tags)
        self.assertEqual(
            e.exception.message,
            'Invalid tag length (should be at least 2 characters)'
        )

    def test_clean_new_experiment_tags(self):

        data = {
            'new_experiment_tags': ' OMICS/protein, omics, complex/Molecule  '
        }
        form = SubmissionTagsForm(data)
        form.is_valid()
        expected = 'complex/molecule,omics,omics/protein'
        self.assertEqual(form.clean_new_experiment_tags(), expected)

    def test_clean_new_analysis_tags(self):

        data = {
            'new_analysis_tags': ' OMICS/protein, omics, complex/Molecule  '
        }
        form = SubmissionTagsForm(data)
        form.is_valid()
        expected = 'complex/molecule,omics,omics/protein'
        self.assertEqual(form.clean_new_analysis_tags(), expected)

    def test_clean(self):

        data = {
            'experiment_tags': ['msms', 'omics/rna'],
            'analysis_tags': ['complex/molecule/atom', 'msms'],
            'new_analysis_tags': 'ijm, candida',
            'new_experiment_tags': 'msms/time, rna-seq',
            'tags': None,
        }

        form = SubmissionTagsForm(data)
        assert form.is_valid()

        expected = {
            'experiment_tags': ['msms', 'omics/rna'],
            'analysis_tags': ['complex/molecule/atom', 'msms'],
            'new_analysis_tags': 'candida,ijm',
            'new_experiment_tags': 'msms/time,rna-seq',
            'tags': None,
        }
        self.assertEqual(form.cleaned_data, expected)

    def test__set_tags(self):

        data = {
            'experiment_tags': ['msms', 'omics/rna'],
            'analysis_tags': ['complex/molecule/atom', 'msms'],
            'new_analysis_tags': 'ijm, candida',
            'new_experiment_tags': 'msms/time, rna-seq',
            'tags': None,
        }
        form = SubmissionTagsForm(data)

        # We cannot set tags on an unvalidated form
        self.assertFalse(hasattr(form, 'cleaned_data'))
        form._set_tags()
        self.assertFalse(hasattr(form, 'cleaned_data'))
        self.assertIsNone(form.instance.tags)

        assert form.is_valid()
        self.assertIsNone(form.cleaned_data['tags'])

        form._set_tags()

        expected = {
            'analysis': 'candida,complex/molecule/atom,ijm,msms',
            'experiment': 'msms,msms/time,omics/rna,rna-seq'
        }
        self.assertEqual(form.cleaned_data['tags'], expected)
        self.assertEqual(form.instance.tags, expected)

    def test_save(self):

        self.assertIsNone(self.process.tags)

        data = {
            'experiment_tags': ['msms', 'omics/rna'],
            'analysis_tags': ['complex/molecule/atom', 'msms'],
            'new_analysis_tags': 'ijm, candida',
            'new_experiment_tags': 'msms/time, rna-seq',
            'tags': {},
        }
        form = SubmissionTagsForm(data, instance=self.process)
        assert form.is_valid()

        expected = {
            'analysis': 'candida,complex/molecule/atom,ijm,msms',
            'experiment': 'msms,msms/time,omics/rna,rna-seq'
        }
        process = form.save()
        self.assertEqual(process.tags, expected)
        self.assertEqual(self.process.tags, expected)
