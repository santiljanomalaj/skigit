# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-05 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailpost', '0014_auto_20180926_0704'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]