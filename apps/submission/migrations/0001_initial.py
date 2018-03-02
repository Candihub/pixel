# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-16 10:28
from __future__ import unicode_literals

import apps.submission.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('viewflow', '0006_i18n'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionProcess',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='viewflow.Process')),
                ('label', models.CharField(help_text="Give this new submission a label so that you'll recover it easily", max_length=150, verbose_name='Label')),
                ('archive', models.FileField(upload_to=apps.submission.models.SubmissionProcess.archive_upload_to, verbose_name='Pixels submitted archive')),
                ('downloaded', models.BooleanField(default=False)),
                ('uploaded', models.BooleanField(default=False)),
                ('validated', models.BooleanField(default=False)),
                ('imported', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('viewflow.process',),
        ),
    ]
