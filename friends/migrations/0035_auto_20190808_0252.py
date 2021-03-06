# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-08 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0034_auto_20190806_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Friends'), ('3', 'Not a Friends'), ('2', 'Remove friend')], default='0', max_length=5, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='friendinvitation',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Friends')], default='0', max_length=5, verbose_name='Status'),
        ),
    ]
