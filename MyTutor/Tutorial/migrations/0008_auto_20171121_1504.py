# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 07:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorial', '0007_profile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
        migrations.AddField(
            model_name='myuser',
            name='profile_content',
            field=models.CharField(default='', max_length=2000),
        ),
    ]
