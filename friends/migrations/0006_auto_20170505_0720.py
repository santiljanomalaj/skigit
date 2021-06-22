# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('friends', '0005_auto_20170327_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brochure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('header_text', models.CharField(max_length=300, null=True, verbose_name=b'Header Text', blank=True)),
                ('poster_1', models.ImageField(upload_to=b'media/skigit/brochure/', null=True, verbose_name=b'Brochure', blank=True)),
            ],
            options={
                'verbose_name': 'Brochure',
                'verbose_name_plural': 'Brochure',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrochureBLogo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('b_logo', models.URLField(null=True, verbose_name=b'Business Logo', blank=True)),
                ('brochure', models.ForeignKey(verbose_name=b'Brochure', blank=True, to='friends.Brochure', null=True)),
                ('user', models.ForeignKey(verbose_name=b'Business User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Brochure Business Logo',
                'verbose_name_plural': 'Brochure Business Logo',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PosterBusinessLogo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('b_logo', models.URLField(null=True, verbose_name=b'Business Logo', blank=True)),
                ('user', models.ForeignKey(verbose_name=b'Business User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Wall Poster Business Logo',
                'verbose_name_plural': 'Wall Poster Business Logo',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WallPoster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('skigit_logo', models.ImageField(upload_to=b'media/skigit/brochure/', null=True, verbose_name=b'Skigit Logo', blank=True)),
                ('poster_1', models.ImageField(upload_to=b'media/skigit/brochure/', null=True, verbose_name=b'Wall Poster 18"x24"', blank=True)),
                ('poster_2', models.ImageField(upload_to=b'media/skigit/brochure/', null=True, verbose_name=b'Wall Poster 24"x36"', blank=True)),
                ('header_image', models.ImageField(null=True, upload_to=b'media/skigit/brochure', blank=True)),
                ('header_text', models.CharField(max_length=300, null=True, verbose_name=b'Header Text', blank=True)),
                ('content1', models.TextField(null=True, verbose_name=b'Content 1', blank=True)),
                ('content2', models.TextField(null=True, verbose_name=b'Content 2', blank=True)),
                ('content3', models.TextField(null=True, verbose_name=b'Content 3', blank=True)),
                ('content4', models.CharField(max_length=500, null=True, verbose_name=b'Skigit URL', blank=True)),
                ('footer_text', models.TextField(max_length=500, null=True, verbose_name=b'Footer Text', blank=True)),
            ],
            options={
                'verbose_name': 'Store Wall Poster',
                'verbose_name_plural': 'Store Wall Poster',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='posterbusinesslogo',
            name='wall_post',
            field=models.ForeignKey(verbose_name=b'Wall Poster', blank=True, to='friends.WallPoster', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='socialsharethumbnail',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 5, 7, 20, 1, 497220, tzinfo=utc), verbose_name=b'Created Date', auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='socialsharethumbnail',
            name='updated_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 5, 7, 20, 13, 630183, tzinfo=utc), verbose_name=b'Updated Date', auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='socialsharethumbnail',
            name='url',
            field=models.URLField(max_length=555),
            preserve_default=True,
        ),
    ]
