# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-15 09:32
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0006_submissionprocess_analysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionprocess',
            name='tags',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Submitted tags for experiment and analysis', null=True, verbose_name='Tags'),
        ),
    ]
