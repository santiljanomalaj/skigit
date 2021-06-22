# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friends', '0003_socialsharethumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now=True, verbose_name='Created Date', auto_created=True)),
                ('message', models.TextField(null=True, verbose_name='Message', blank=True)),
                ('skigit_id', models.IntegerField(null=True, verbose_name='Skigit_id', blank=True)),
                ('msg_type', models.CharField(db_index=True, max_length='30', null=True, verbose_name='Message Type', blank=True)),
                ('is_read', models.BooleanField(default=False, verbose_name='Read by User')),
                ('is_view', models.BooleanField(default=False, verbose_name='Viewed by User')),
                ('is_active', models.BooleanField(default=True, verbose_name='Deleted by User')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
                ('from_user', models.ForeignKey(related_name='Notification sender user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
            },
        ),
        migrations.AlterIndexTogether(
            name='notification',
            index_together=set([('skigit_id', 'user', 'from_user', 'is_view', 'is_active')]),
        ),
        migrations.AlterIndexTogether(
            name='friend',
            index_together=set([('from_user', 'status', 'is_active'), ('to_user', 'status', 'is_active')]),
        ),
    ]
