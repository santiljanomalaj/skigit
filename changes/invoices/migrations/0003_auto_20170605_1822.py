# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_auto_20170517_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='billing_agreement_id',
            field=models.CharField(max_length=150, null=True, verbose_name=b'Billing Agreement ID', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='email',
            field=models.EmailField(max_length=75, null=True, verbose_name=b'PayPal Email', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='invoice',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name=b'Is Credit Card/ PayPal Account Deleted'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='cardholder_name',
            field=models.CharField(max_length=250, null=True, verbose_name=b'Card Holder Name', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='customer_id',
            field=models.CharField(max_length=100, verbose_name=b'Customer id'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='first_6',
            field=models.PositiveIntegerField(null=True, verbose_name=b'first 6 Numbers (bin)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='issuing_bank',
            field=models.CharField(max_length=250, null=True, verbose_name=b'Issuing Bank', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='last_4',
            field=models.PositiveSmallIntegerField(null=True, verbose_name=b'Last 4 Numbers', blank=True),
            preserve_default=True,
        ),
    ]
