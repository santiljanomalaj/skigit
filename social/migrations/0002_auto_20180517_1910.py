# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-17 19:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skigit', '0001_initial'),
        ('social', '0001_initial'),
    ]

    operations = []
