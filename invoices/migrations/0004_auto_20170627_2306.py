# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0003_auto_20170605_1822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billing',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='billing',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='Billing',
        ),
    ]
