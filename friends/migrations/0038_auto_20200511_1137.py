# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-05-11 06:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0037_auto_20190813_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('3', 'Not a Friends'), ('2', 'Remove friend'), ('1', 'Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
    ]
