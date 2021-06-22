# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-25 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailpost', '0012_emailtemplate_template_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='html_template',
            field=models.TextField(default='defu'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='subject',
            field=models.CharField(default='defu', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailtemplate',
            name='template_name',
            field=models.CharField(default='defu', max_length=255),
            preserve_default=False,
        ),
    ]
