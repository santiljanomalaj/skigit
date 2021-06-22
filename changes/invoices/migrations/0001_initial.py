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
            name='BusinessLogoInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('logo_count', models.IntegerField(default=0, verbose_name=b'Logo PPV Count')),
                ('logo_total_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('logo_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('total_logo_count', models.IntegerField(default=0, verbose_name=b'Total Count (PPV)')),
                ('user_total_due', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('business_logo', models.ForeignKey(related_name='Business Logo', blank=True, to='user.BusinessLogo', null=True)),
                ('logo_user', models.ForeignKey(related_name='logo_viewer_user', verbose_name=b'Business Logo User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='business_logo_user', verbose_name=b'Business Logo Visitor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Business Logo Invoice',
                'verbose_name_plural': 'Business Logo Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmbedInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('embed_count', models.IntegerField(null=True, verbose_name=b'Embed Count', blank=True)),
                ('embed_total_amount', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('skigit_embed_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('embed_total_count', models.IntegerField(null=True, verbose_name=b'Total Count', blank=True)),
                ('embed_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('embed_ski', models.ForeignKey(blank=True, to='skigit.VideoDetail', null=True)),
                ('skigit_user', models.ForeignKey(related_name='skigit_embed_user', verbose_name=b'Skigit User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='embed_business_user', verbose_name=b'Business User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Embed Invoice',
                'verbose_name_plural': 'Embed Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PluginInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('plugin_count', models.IntegerField(default=0, verbose_name=b'Plugin Count', blank=True)),
                ('current_plugin_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('plugin_total_amount', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('plugin_total_count', models.IntegerField(default=0, verbose_name=b'Total Count', blank=True)),
                ('plug_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('plugin_ski', models.ForeignKey(related_name='primary_ski', verbose_name=b'Plugged Skigit', blank=True, to='skigit.VideoDetail', null=True)),
                ('primary_ski', models.ForeignKey(related_name='plug_ski', verbose_name=b'Skigit', blank=True, to='skigit.VideoDetail', null=True)),
                ('skigit_user', models.ForeignKey(related_name='skigit_plugin_user', verbose_name=b'Skigit Logo User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='business_plugin_user', verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Plugin Invoice',
                'verbose_name_plural': 'Plugin Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PostInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('post_count', models.IntegerField(null=True, verbose_name=b'Post Count', blank=True)),
                ('skigit_post_amount', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('post_total_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('post_total_count', models.IntegerField(null=True, verbose_name=b'Total Count', blank=True)),
                ('social_network_type', models.CharField(max_length=500, null=True, verbose_name=b'Social Network Type', blank=True)),
                ('post_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('logo_user', models.ForeignKey(related_name='b_logo_user', verbose_name=b'Logo User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('post_ski', models.ForeignKey(blank=True, to='skigit.VideoDetail', null=True)),
                ('user', models.ForeignKey(related_name='business_post_user', verbose_name=b'Post User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Post Invoice',
                'verbose_name_plural': 'Post Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShareInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('share_count', models.IntegerField(null=True, verbose_name=b'Share Count', blank=True)),
                ('share_total_amount', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('skigit_share_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('total_share_count', models.IntegerField(null=True, verbose_name=b'Total Count', blank=True)),
                ('share_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('share_ski', models.ForeignKey(blank=True, to='skigit.VideoDetail', null=True)),
                ('skigit_user', models.ForeignKey(related_name='skigit_share_user', verbose_name=b'Skigit User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='business_share_user', verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Share Invoice',
                'verbose_name_plural': 'Share Invoice',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VisitCharges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, auto_created=True)),
                ('logo_charge', models.DecimalField(default=0.29, verbose_name=b'Logo PPV Charge', max_digits=9, decimal_places=2, blank=True)),
                ('link_charge', models.DecimalField(default=1.99, verbose_name=b'Web Link Charge', max_digits=9, decimal_places=2, blank=True)),
                ('plug_charge', models.DecimalField(default=0.29, verbose_name=b'Plugin Charge', max_digits=9, decimal_places=2, blank=True)),
                ('post_charge', models.DecimalField(default=0.79, verbose_name=b'Post Charge', max_digits=9, decimal_places=2, blank=True)),
                ('share_charge', models.DecimalField(default=0.49, verbose_name=b'Share Charge', max_digits=9, decimal_places=2, blank=True)),
                ('embed_charge', models.DecimalField(default=49.0, verbose_name=b'Embed Charge', max_digits=9, decimal_places=2, blank=True)),
                ('user', models.ForeignKey(related_name='superuse_payment', verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WebLinkInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_date', models.DateTimeField(auto_now=True, auto_created=True)),
                ('billing_month', models.DateField(auto_now_add=True, auto_created=True)),
                ('web_link', models.URLField(null=True, verbose_name=b'Awesome Company Links', blank=True)),
                ('link_count', models.IntegerField(default=0, verbose_name=b'Links Count')),
                ('link_due_amount', models.DecimalField(default=0.0, verbose_name=b'Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('link_total_due', models.DecimalField(default=0.0, verbose_name=b'Total Due Amount($)', max_digits=9, decimal_places=2, blank=True)),
                ('link_total_count', models.IntegerField(default=0, verbose_name=b'Total Count')),
                ('link_is_paid', models.BooleanField(default=False, verbose_name=b'Amount Paid')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(related_name='link_visitor_user', verbose_name=b'Business User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('web_link_user', models.ForeignKey(related_name='web_link_user', verbose_name=b'Web Link User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Awesome Web link Invoice',
                'verbose_name_plural': 'Awesome Web link Invoice',
            },
            bases=(models.Model,),
        ),
    ]
