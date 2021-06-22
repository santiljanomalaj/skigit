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
            model_name='businesslogoinvoice',
            name='business_logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='BusinessLogo', to='skigit.BusinessLogo'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='logo_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logo_viewer_user', to=settings.AUTH_USER_MODEL, verbose_name='Business Logo User'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_logo_user', to=settings.AUTH_USER_MODEL, verbose_name='Business Logo Visitor'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plugin_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ski', to='skigit.VideoDetail', verbose_name='Plugged Skigit'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='primary_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plug_ski', to='skigit.VideoDetail', verbose_name='Skigit'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='skigit_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skigit_plugin_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit Logo User'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_plugin_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='logo_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b_logo_user', to=settings.AUTH_USER_MODEL, verbose_name='Logo User'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='skigit.VideoDetail'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_post_user', to=settings.AUTH_USER_MODEL, verbose_name='Post User'),
        ),
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