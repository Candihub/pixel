# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-18 09:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20171213_1009'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entry',
            unique_together=set([('identifier', 'repository')]),
        ),
    ]
