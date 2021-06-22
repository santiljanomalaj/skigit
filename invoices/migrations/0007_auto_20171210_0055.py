# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-10 00:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0006_auto_20171210_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='link_visitor_user', to=settings.AUTH_USER_MODEL, verbose_name='Business User'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='web_link_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='web_link_user', to=settings.AUTH_USER_MODEL, verbose_name='Web Link User'),
        ),
    ]