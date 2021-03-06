# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-17 18:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sperks', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BugReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_date', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='Report updated date')),
                ('created_date', models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name='Report created date')),
                ('user', models.CharField(blank=True, max_length=300, null=True, verbose_name='User')),
                ('bug_title', models.CharField(blank=True, max_length=300, null=True, verbose_name='Title')),
                ('bug_page_url', models.URLField(blank=True, null=True, verbose_name='URL')),
                ('bug_description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('bug_comment', models.TextField(blank=True, null=True, verbose_name='Comments')),
                ('bug_status', models.IntegerField(blank=True, choices=[(0, 'Open'), (1, 'Under investigation'), (2, 'Closed')], default=0, null=True, verbose_name='Status')),
                ('bug_repeated', models.BooleanField(default=False, verbose_name='Bug repeated')),
                ('bug_repeated_count', models.IntegerField(blank=True, default=0, null=True, verbose_name='Bug repeated count')),
            ],
            options={
                'verbose_name': 'Bug Report Management',
                'verbose_name_plural': 'Bug Report Management',
            },
        ),
        migrations.CreateModel(
            name='CopyRightInfringement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_date', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='Report updated date')),
                ('created_date', models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name='Report created date')),
                ('complaint_date', models.DateField(auto_created=True, auto_now=True, verbose_name='Complaint Date')),
                ('skigit_id', models.IntegerField(blank=True, null=True, verbose_name='Infringed work on Skigit')),
                ('urls', models.URLField(verbose_name='My Website Urls')),
                ('description', models.TextField(verbose_name='Description')),
                ('address', models.CharField(max_length=500, verbose_name='Street Address')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('state', models.CharField(max_length=200, verbose_name='State/Province')),
                ('zip_code', models.IntegerField(blank=True, null=True, verbose_name='Zip/Postal Code')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('phone', models.CharField(max_length=200, verbose_name='Phone Number')),
                ('email', models.EmailField(max_length=200, verbose_name='Email Address')),
                ('submitter_request', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=None, verbose_name='Submitter Request Remove all')),
                ('full_name', models.CharField(max_length=500, verbose_name='Full name')),
                ('signature', models.CharField(blank=True, max_length=200, null=True, verbose_name='Electronic Signature')),
                ('status', models.IntegerField(blank=True, choices=[(0, 'Open'), (1, 'Under investigation'), (2, 'Closed'), (3, 'Remove Skigit')], default=0, null=True, verbose_name='Investigation Status')),
                ('submitted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaint_by_register_user', to='user.Profile', verbose_name='Submitted by')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='infringement_copytight_user', to=settings.AUTH_USER_MODEL, verbose_name='Submitted by User')),
            ],
            options={
                'verbose_name': 'Copyright Infringement',
                'verbose_name_plural': 'Copyright Infringement',
            },
        ),
        migrations.CreateModel(
            name='CopyRightInvestigation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_date', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='Investigation updated date')),
                ('created_date', models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name='Investigation created date')),
                ('remove_all', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Remove all')),
                ('strike', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Strike')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Investigation Description and conclusion')),
                ('action', models.TextField(blank=True, null=True, verbose_name='Action Taken')),
                ('copy_right', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='skigit.CopyRightInfringement', verbose_name='Copy Right Infringement')),
                ('investigator_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_investigator_name', to='user.Profile', verbose_name='Investigator Name')),
            ],
            options={
                'verbose_name': 'Copyright Investigation',
                'verbose_name_plural': 'Copyright Investigation',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('status', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
            options={
                'verbose_name': 'Favorite/Unfavorite Skigit',
                'verbose_name_plural': 'Favorite/Unfavorite Skigits',
            },
        ),
        migrations.CreateModel(
            name='InappropriateSkigit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('action', models.CharField(choices=[('0', 'Pending'), ('1', 'Appropriate'), ('2', 'Inappropriate')], default='0', max_length=20, verbose_name='Action')),
                ('status', models.CharField(choices=[('1', 'Open'), ('2', 'Under Investigation'), ('3', 'Closed'), ('4', 'Remove Skigit')], default='1', max_length=20, verbose_name='Status')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
            options={
                'verbose_name': 'Inappropriate Skigit',
                'verbose_name_plural': 'Inappropriate Skigits',
            },
        ),
        migrations.CreateModel(
            name='InappropriateSkigitInvestigator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('result_remove_all', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False)),
                ('result_strike', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False)),
                ('investigation_discription', models.TextField(blank=True, null=True, verbose_name='Investigation Description and conclusion')),
                ('action_taken', models.TextField(blank=True, null=True, verbose_name='Action Taken')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('inapp_skigit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inappskigit', to='skigit.InappropriateSkigit', verbose_name='Inappropriate Skigit')),
                ('investigating_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Investigating_User', to=settings.AUTH_USER_MODEL, verbose_name='Investigating User')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'Inappropriate skigit Investigator',
                'verbose_name_plural': 'Inappropriate skigit Investigator',
            },
        ),
        migrations.CreateModel(
            name='InappropriateSkigitReason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('reason_title', models.CharField(max_length=100, unique=True, verbose_name='Reason Title')),
                ('reason_slug', models.SlugField(max_length=100, unique=True, verbose_name='Reason Slug')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'Inappropriate skigit Reason',
                'verbose_name_plural': 'Inappropriate Skigit Reasons',
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('status', models.BooleanField(default=True)),
                ('is_read', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
            options={
                'verbose_name': 'Like/Unlike Skigit',
                'verbose_name_plural': 'Like/Unlike Skigits',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Account Email ID')),
                ('payment_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Account Holder Name')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payment',
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_on_server', models.FileField(help_text='Temporary file on server for using in `direct upload` from your server to youtube', null=True, upload_to='videos')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedVideoLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_link', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('title', models.CharField(db_index=True, max_length=200, verbose_name='My Skigit Title')),
                ('video_id', models.CharField(help_text='The Youtube id of the video', max_length=255, null=True, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('youtube_url', models.URLField(blank=True, max_length=255, null=True)),
                ('swf_url', models.URLField(blank=True, max_length=255, null=True)),
                ('access_control', models.SmallIntegerField(choices=[(0, 'Public'), (1, 'Unlisted'), (2, 'Private')], default=1)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_user_auth1', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VideoDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('title', models.CharField(error_messages={'unique': 'This name already exists.'}, max_length=40, unique=True, verbose_name='My Skigit Title')),
                ('made_by_option', models.CharField(blank=True, default='', max_length=200, verbose_name='If not found in the list above, add maker or proprietor name')),
                ('bought_at', models.URLField(max_length=255)),
                ('add_logo', models.IntegerField(choices=[(1, 'Yes'), (0, 'No')], default=1)),
                ('why_rocks', models.TextField(default='', max_length=200)),
                ('status', models.IntegerField(default=0, verbose_name='Status')),
                ('is_share', models.BooleanField(default=False)),
                ('inappropriate_skigit', models.CharField(blank=True, choices=[('0', 'Pending'), ('1', 'Appropriate'), ('2', 'Inappropriate')], max_length=5, null=True, verbose_name='Inappropriate')),
                ('is_plugged', models.BooleanField(default=False, verbose_name='Plugged')),
                ('is_sperk', models.BooleanField(default=False, verbose_name='Sperk')),
                ('receive_donate_sperk', models.IntegerField(choices=[(2, 'Receive sperk'), (1, 'Donate sperk')], default=0, verbose_name='Sperk choice')),
                ('view_count', models.IntegerField(blank=True, default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('copyright_skigit', models.CharField(blank=True, choices=[('0', 'Open'), ('1', 'Under Investigation'), ('2', 'Closed'), ('3', 'Remove Skigit')], default=None, max_length=5, null=True, verbose_name='Copyright Infringement')),
                ('business_logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='associated_business_user', to='user.BusinessLogo')),
                ('business_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skigit_business_user', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('donate_skigit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donation_skigit', to='sperks.Donation', verbose_name='Donation Organization')),
                ('incentive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sperks.Incentive')),
                ('made_by', models.ForeignKey(blank=True, help_text='Select maker', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video_made_by', to=settings.AUTH_USER_MODEL, verbose_name='My awesome thing was made by')),
                ('plugged_skigit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plugged_skigit', to='skigit.Video', verbose_name='Plugged Skigit')),
                ('share_skigit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videodetail_requests_created', to='skigit.Video')),
                ('skigit_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='skigit.Video')),
                ('subject_category', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='core.SubjectCategory', verbose_name='My Subject Category')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
            ],
            options={
                'verbose_name': 'Skigit',
                'verbose_name_plural': 'Skigits',
                'ordering': ('created_date',),
            },
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='thumbnails', to='skigit.Video'),
        ),
        migrations.AddField(
            model_name='like',
            name='skigit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='skigit.Video'),
        ),
        migrations.AddField(
            model_name='like',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='inappropriateskigit',
            name='reason',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Inappropriate_Skigit_Reason', to='skigit.InappropriateSkigitReason', verbose_name='Inappropriate Reason'),
        ),
        migrations.AddField(
            model_name='inappropriateskigit',
            name='reported_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Reported_User', to=settings.AUTH_USER_MODEL, verbose_name='Reported User'),
        ),
        migrations.AddField(
            model_name='inappropriateskigit',
            name='skigit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Skigit', to='skigit.VideoDetail', verbose_name='Skigit'),
        ),
        migrations.AddField(
            model_name='inappropriateskigit',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='skigit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourites', to='skigit.Video'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bugreport',
            name='skigit_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bug_report_skigit', to='skigit.VideoDetail', verbose_name='Skigit'),
        ),
        migrations.AlterIndexTogether(
            name='videodetail',
            index_together=set([('status', 'is_active'), ('status', 'is_active', 'plugged_skigit', 'is_plugged')]),
        ),
        migrations.AlterIndexTogether(
            name='like',
            index_together=set([('skigit', 'user', 'status')]),
        ),
        migrations.AlterIndexTogether(
            name='favorite',
            index_together=set([('skigit', 'status', 'is_active')]),
        ),
    ]
