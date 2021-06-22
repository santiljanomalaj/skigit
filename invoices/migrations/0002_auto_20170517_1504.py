# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invoice_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Invoice Date')),
                ('pay_amount', models.DecimalField(default=0.0, verbose_name=b'Payable Amount', max_digits=9, decimal_places=2, blank=True)),
                ('payed_amount', models.DecimalField(default=0.0, verbose_name=b'Payed Amount', max_digits=9, decimal_places=2, blank=True)),
                ('payment_status', models.BooleanField(default=False, verbose_name=b'Payment Received', choices=[(False, b'Pending'), (True, b'Payed')])),
                ('pay_method', models.CharField(default=b'0', max_length=5, verbose_name=b'Payment Method', choices=[(b'0', b'PayPal'), (b'1', b'Credit/Debit Card')])),
                ('transaction_id', models.CharField(max_length=500, null=True, verbose_name=b'Transaction id', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Created date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name=b'Updated date', auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Billing Info',
                'verbose_name_plural': 'Billing Info',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='billing',
            name='invoice',
            field=models.ForeignKey(related_name='billing_id_of_customer', verbose_name=b'Invoice Vault', to='invoices.Invoice'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billing',
            name='user_id',
            field=models.ForeignKey(related_name='billing_user', verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='businesslogoinvoice',
            options={'verbose_name': 'Business Logo Invoice', 'verbose_name_plural': 'Business Logo Invoices'},
        ),
        migrations.AlterModelOptions(
            name='embedinvoice',
            options={'verbose_name': 'Embed Invoice', 'verbose_name_plural': 'Embed Invoices'},
        ),
        migrations.AlterModelOptions(
            name='plugininvoice',
            options={'verbose_name': 'Plugin Invoice', 'verbose_name_plural': 'Plugin Invoices'},
        ),
        migrations.AlterModelOptions(
            name='postinvoice',
            options={'verbose_name': 'Post Invoice', 'verbose_name_plural': 'Post Invoices'},
        ),
        migrations.AlterModelOptions(
            name='shareinvoice',
            options={'verbose_name': 'Share Invoice', 'verbose_name_plural': 'Share Invoices'},
        ),
        migrations.AlterModelOptions(
            name='visitcharges',
            options={'verbose_name': 'Business Charge', 'verbose_name_plural': 'Business Charges'},
        ),
        migrations.AlterModelOptions(
            name='weblinkinvoice',
            options={'verbose_name': 'Awesome Web link Invoice', 'verbose_name_plural': 'Awesome Web link Invoices'},
        ),
    ]
