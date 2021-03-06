# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-02-02 12:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skigit', '0008_auto_20210202_1357'),
        ('invoices', '0012_auto_20200511_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewInvoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_month', models.DateField(auto_created=True, auto_now_add=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('view_count', models.IntegerField(blank=True, null=True, verbose_name='View Count')),
                ('skigit_view_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)')),
                ('view_total_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)')),
                ('total_view_count', models.IntegerField(blank=True, null=True, verbose_name='Total Count')),
                ('view_is_paid', models.BooleanField(default=False, verbose_name='Amount Paid')),
                ('view_page', models.IntegerField(choices=[(0, 'Detail'), (1, 'Main')], default=0)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('skigit_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_skigit_view_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit User')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skigit_view_user', to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('view_ski', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='skigit.VideoDetail')),
            ],
            options={
                'verbose_name': 'View Invoice',
                'verbose_name_plural': 'View Invoices',
            },
        ),
        migrations.AlterModelOptions(
            name='weblinkinvoice',
            options={'verbose_name': 'Web link Invoice', 'verbose_name_plural': 'Web link Invoices'},
        ),
        migrations.AlterField(
            model_name='learnmoreinvoice',
            name='current_learn_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Current Learn more Amount($)'),
        ),
    ]
