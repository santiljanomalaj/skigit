# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-13 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0036_auto_20190808_0256'),
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
            field=models.CharField(choices=[('3', 'Not a Friends'), ('2', 'Remove friend'), ('0', 'Pending'), ('1', 'Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='friendinvitation',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
    ]
