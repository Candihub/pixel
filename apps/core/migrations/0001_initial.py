# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-11 14:07
from __future__ import unicode_literals

import apps.core.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import tagulous.models.fields
import tagulous.models.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pixeler',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Analysis',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('secondary_data', models.FileField(upload_to=apps.core.models.Analysis.secondary_data_upload_to, verbose_name='Secondary data')),
                ('notebook', models.FileField(blank=True, help_text='Upload your Jupiter Notebook or any other document helping to understand your analysis', upload_to=apps.core.models.Analysis.notebook_upload_to, verbose_name='Notebook')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('saved_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Analysis',
                'verbose_name_plural': 'Analyses',
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('released_at', models.DateField(verbose_name='Release date')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('saved_at', models.DateTimeField(auto_now=True)),
                ('entries', models.ManyToManyField(related_name='experiments', related_query_name='experiment', to='data.Entry')),
            ],
            options={
                'verbose_name': 'Experiment',
                'verbose_name_plural': 'Experiments',
            },
        ),
        migrations.CreateModel(
            name='OmicsArea',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.OmicsArea')),
            ],
            options={
                'verbose_name': 'Omics area',
                'verbose_name_plural': 'Omics areas',
            },
        ),
        migrations.CreateModel(
            name='OmicsUnit',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Dubious'), (2, 'Exists'), (3, 'Invalid'), (4, 'Validated')], default=1, verbose_name='Status')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Entry')),
            ],
            options={
                'verbose_name': 'Omics Unit',
                'verbose_name_plural': 'Omics Units',
            },
        ),
        migrations.CreateModel(
            name='OmicsUnitType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Omics unit type',
                'verbose_name_plural': 'Omics unit types',
            },
        ),
        migrations.CreateModel(
            name='Pixel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('value', models.FloatField(help_text='The pixel value', verbose_name='Value')),
                ('quality_score', models.FloatField(blank=True, help_text='Could be a p-value, confidence index, etc.', null=True, verbose_name='Quality score')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pixels', related_query_name='pixel', to='core.Analysis')),
                ('omics_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pixels', related_query_name='pixel', to='core.OmicsUnit')),
            ],
            options={
                'verbose_name': 'Pixel',
                'verbose_name_plural': 'Pixels',
            },
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='species', related_query_name='species', to='data.Entry')),
            ],
            options={
                'verbose_name': 'Species',
                'verbose_name_plural': 'Species',
            },
        ),
        migrations.CreateModel(
            name='Strain',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strains', related_query_name='strain', to='core.Species')),
            ],
            options={
                'verbose_name': 'Strain',
                'verbose_name_plural': 'Strains',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField()),
                ('count', models.IntegerField(default=0, help_text='Internal counter of how many times this tag is in use')),
                ('protected', models.BooleanField(default=False, help_text='Will not be deleted when the count reaches 0')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
            bases=(tagulous.models.models.BaseTagModel, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='omicsunit',
            name='strain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='omics_units', related_query_name='omics_unit', to='core.Strain'),
        ),
        migrations.AddField(
            model_name='omicsunit',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='omics_units', related_query_name='omics_unit', to='core.OmicsUnitType'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='omics_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiments', related_query_name='experiment', to='core.OmicsArea'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='tags',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, help_text='Enter a comma-separated tag string', to='core.Tag'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='experiments',
            field=models.ManyToManyField(related_name='analyses', related_query_name='analysis', to='core.Experiment'),
        ),
        migrations.AddField(
            model_name='analysis',
            name='pixeler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analyses', related_query_name='analysis', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='analysis',
            name='tags',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, help_text='Enter a comma-separated tag string', to='core.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='strain',
            unique_together=set([('name', 'species')]),
        ),
        migrations.AlterUniqueTogether(
            name='omicsunit',
            unique_together=set([('reference', 'strain', 'type')]),
        ),
    ]
