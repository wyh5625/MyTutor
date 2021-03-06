# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 12:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Tutorial', '0008_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='cashflow',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='information',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Tutorial.TutorialSession'),
        ),
    ]
