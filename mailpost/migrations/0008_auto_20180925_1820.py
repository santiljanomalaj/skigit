# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-25 18:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailpost', '0007_remove_emailbody_is_html'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EmailBody',
            new_name='EmailTemplate',
        ),
    ]
