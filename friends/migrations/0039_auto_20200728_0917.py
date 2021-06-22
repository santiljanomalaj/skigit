# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2020-07-28 09:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0038_auto_20200511_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='embed',
            name='embed_type',
            field=models.CharField(choices=[('1', 'External'), ('0', 'Internal')], default='0', max_length=5, verbose_name='Embed Type'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('2', 'Remove friend'), ('1', 'Friends'), ('3', 'Not a Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
    ]