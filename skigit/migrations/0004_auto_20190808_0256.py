# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-08 02:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skigit', '0003_auto_20190806_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thumbnail',
            name='filename',
            field=models.URLField(default='', max_length=300),
        ),
    ]