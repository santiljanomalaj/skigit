# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friends', '0004_auto_20170306_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='Embed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('is_embed', models.BooleanField(default=True)),
                ('embed_count', models.IntegerField(default=0, verbose_name=b'Embed Count')),
                ('embed_type', models.CharField(default=b'0', max_length=5, verbose_name=b'Embed Type', choices=[(b'0', b'Internal'), (b'1', b'External')])),
                ('from_user', models.ForeignKey(related_name='embed_from_user', verbose_name=b'From User', to=settings.AUTH_USER_MODEL)),
                ('skigit_id', models.ForeignKey(related_name='embed_video_id', verbose_name=b'Skigit', to='skigit.Video')),
                ('to_user', models.ForeignKey(related_name='embed_to_user', verbose_name=b'To User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Embed',
                'verbose_name_plural': 'Embed',
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='embed',
            index_together=set([('from_user', 'embed_type', 'is_embed'), ('to_user', 'embed_type', 'is_embed')]),
        ),
    ]
