# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 17:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorial', '0013_auto_20171122_0034'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyTutor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Tutorial.Wallet')),
            ],
        ),
    ]
