# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('skigit', '__first__'),
        ('friends', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='is_read',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='friend',
            name='from_user',
            field=models.ForeignKey(related_name='from_user', verbose_name=b'From User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='friend',
            name='to_user',
            field=models.ForeignKey(related_name='to_user', verbose_name=b'To User', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]