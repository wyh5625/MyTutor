# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorial', '0025_merge_20171125_0159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tutor',
            name='reviewd_times',
        ),
        migrations.AlterField(
            model_name='myuser',
            name='image',
            field=models.ImageField(default='profile_image/default.jpg', upload_to='profile_image'),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='showProfile',
            field=models.BooleanField(default=False),
        ),
    ]