# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0002_auto_20161212_1355'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialShareThumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('video', models.ForeignKey(related_name='social_share_thumbnails', to='skigit.Video', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
