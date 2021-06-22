# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('status', models.CharField(default=b'0', max_length=5, verbose_name=b'Status', choices=[(b'3', b'Not a Friends'), (b'1', b'Friends'), (b'0', b'Pending'), (b'2', b'Remove friend')])),
                ('is_active', models.BooleanField(default=True)),
                ('from_user', models.ForeignKey(related_name='From_friend', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(related_name='To_friend', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Friend',
                'verbose_name_plural': 'Friends',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FriendInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('invited_date', models.DateField(auto_now_add=True, verbose_name=b'Invitation Date', auto_created=True)),
                ('to_user_email', models.EmailField(max_length=75, verbose_name=b'Email')),
                ('is_member', models.BooleanField(default=False, verbose_name=b'Is Skigit Member')),
                ('status', models.CharField(default=b'0', max_length=5, verbose_name=b'Status', choices=[(b'0', b'Pending'), (b'1', b'Friends')])),
                ('from_user', models.ForeignKey(related_name='User Invitation', verbose_name=b'Invited by User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Friends Invite',
                'verbose_name_plural': 'Friends Invite',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InviteMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name=b'Message Updated Date', auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Message Created Date', auto_created=True)),
                ('invite_message', models.TextField(null=True, verbose_name=b'Invite Message', blank=True)),
            ],
            options={
                'verbose_name': 'Friends Invitation Message',
                'verbose_name_plural': 'Friends Invitation Message',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='friendinvitation',
            name='invite_text',
            field=models.ForeignKey(verbose_name=b'Invite Message', blank=True, to='friends.InviteMessage', null=True),
            preserve_default=True,
        ),
    ]
