# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-06 00:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skigit', '0002_copyrightinfringement_copyrightinvestigation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thumbnail',
            name='url',
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='file_id',
            field=models.URLField(default='', max_length=300),
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='filename',
            field=models.URLField(default='', max_length=44),
        ),
        migrations.AddField(
            model_name='video',
            name='filename',
            field=models.CharField(help_text='The B2 name file from Backblaze', max_length=44, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_id',
            field=models.CharField(help_text='The B2 id file from Backblaze', max_length=255, null=True, unique=True),
        ),
    ]