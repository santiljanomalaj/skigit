# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-19 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0031_auto_20181006_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='embed',
            name='embed_type',
            field=models.CharField(choices=[('0', 'Internal'), ('1', 'External')], default='0', max_length=5, verbose_name='Embed Type'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='status',
            field=models.CharField(choices=[('2', 'Remove friend'), ('0', 'Pending'), ('1', 'Friends'), ('3', 'Not a Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='friendinvitation',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
    ]
