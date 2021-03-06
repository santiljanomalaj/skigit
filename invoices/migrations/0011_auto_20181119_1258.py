# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-11-19 12:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skigit', '0002_copyrightinfringement_copyrightinvestigation'),
        ('invoices', '0010_merge_20181006_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalEmbedInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_month', models.DateField(auto_created=True, auto_now_add=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('embed_count', models.IntegerField(blank=True, null=True, verbose_name='Embed Count')),
                ('embed_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)')),
                ('skigit_embed_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)')),
                ('embed_total_count', models.IntegerField(blank=True, null=True, verbose_name='Total Count')),
                ('embed_is_paid', models.BooleanField(default=False, verbose_name='Amount Paid')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('embed_ski', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='skigit.VideoDetail')),
                ('skigit_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skigit_internal_embed_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit User')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='internal_embed_business_user', to=settings.AUTH_USER_MODEL, verbose_name='Business User')),
            ],
            options={
                'verbose_name': 'Internal Embed Invoice',
                'verbose_name_plural': 'Internal Embed Invoices',
            },
        ),
        migrations.CreateModel(
            name='LearnMoreInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_month', models.DateField(auto_created=True, auto_now_add=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('learn_count', models.IntegerField(blank=True, null=True, verbose_name='Learn More Count')),
                ('learn_due_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)')),
                ('learn_total_due', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)')),
                ('current_learn_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)')),
                ('learn_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)')),
                ('learn_total_count', models.IntegerField(blank=True, null=True, verbose_name='Total Count')),
                ('learn_is_paid', models.BooleanField(default=False, verbose_name='Amount Paid')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('learn_ski', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='skigit.VideoDetail')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_learn_more_user', to=settings.AUTH_USER_MODEL, verbose_name='Learn More User')),
            ],
            options={
                'verbose_name': 'Learn More Link Invoice',
                'verbose_name_plural': 'Learn More Link Invoices',
            },
        ),
        migrations.AlterModelOptions(
            name='embedinvoice',
            options={'verbose_name': 'Embed External Invoice', 'verbose_name_plural': 'Embed External Invoices'},
        ),
        migrations.AlterModelOptions(
            name='weblinkinvoice',
            options={'verbose_name': 'Learn More link Invoice', 'verbose_name_plural': 'Learn More link Invoices'},
        ),
    ]
