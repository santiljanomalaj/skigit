# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0003_auto_20170605_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceBilling',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pay_amount', models.DecimalField(default=0.0, verbose_name=b'Payable Amount', max_digits=9, decimal_places=2, blank=True)),
                ('payed_amount', models.DecimalField(default=0.0, verbose_name=b'Payed Amount', max_digits=9, decimal_places=2, blank=True)),
                ('payment_status', models.BooleanField(default=False, verbose_name=b'Payment Received', choices=[(False, b'Pending'), (True, b'Payed')])),
                ('pay_method', models.CharField(default=b'0', max_length=5, verbose_name=b'Payment Method', choices=[(b'0', b'PayPalAccount'), (b'1', b'CreditCard')])),
                ('pay_mnth', models.CharField(max_length=2, verbose_name=b'Pay Month')),
                ('pay_yr', models.CharField(max_length=4, verbose_name=b'Pay Year')),
                ('transaction_id', models.CharField(max_length=500, null=True, verbose_name=b'Transaction id', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Created date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name=b'Updated date', auto_now_add=True)),
                ('invoice', models.ForeignKey(related_name='invoices_billing', verbose_name=b'Invoice Vault', to='invoices.Invoice')),
                ('user_id', models.ForeignKey(related_name='billing_user', verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Billing Info',
                'verbose_name_plural': 'Billing Info',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='billing',
            name='invoice',
        ),
        migrations.RemoveField(
            model_name='billing',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='Billing',
        ),
    ]
