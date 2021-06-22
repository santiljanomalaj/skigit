# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-22 22:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('customer_id', models.CharField(max_length=100, verbose_name='Customer id')),
                ('customer_location', models.CharField(blank=True, max_length=250, null=True, verbose_name='Customer Location')),
                ('type', models.CharField(blank=True, max_length=50, null=True, verbose_name='Type')),
                ('payment_method_token', models.CharField(max_length=300, verbose_name='Customer token')),
                ('c_image_url', models.URLField(blank=True, null=True, verbose_name='Card Type Image')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='PayPal Email')),
                ('billing_agreement_id', models.CharField(blank=True, max_length=150, null=True, verbose_name='Billing Agreement ID')),
                ('last_4', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Last 4 Numbers')),
                ('first_6', models.PositiveIntegerField(blank=True, null=True, verbose_name='first 6 Numbers (bin)')),
                ('cardholder_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Card Holder Name')),
                ('debit', models.CharField(blank=True, max_length=300, null=True, verbose_name='Debit')),
                ('issuing_bank', models.CharField(blank=True, max_length=250, null=True, verbose_name='Issuing Bank')),
                ('country_of_issuance', models.CharField(blank=True, max_length=250, null=True, verbose_name='Country of Issuance')),
                ('card_status', models.CharField(blank=True, max_length=250, null=True, verbose_name='Card Status')),
                ('cvv_response_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='CVV Response Code')),
                ('currency_iso_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='Currency iso Code')),
                ('credit_card_type', models.CharField(blank=True, max_length=200, null=True, verbose_name='Credit/Debit Card Type')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Credit Card/ PayPal Account Deleted')),
                ('merchant_account_id', models.URLField(blank=True, null=True, verbose_name='Merchant Account id')),
                ('unique_number_identifier', models.CharField(blank=True, max_length=500, null=True, verbose_name='Unique Identifier Number')),
                ('processor_response_code', models.CharField(blank=True, max_length=500, null=True, verbose_name='Processor Response Code')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_user', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Invoice Vault',
                'verbose_name_plural': 'Invoices Vault',
            },
        ),
        migrations.CreateModel(
            name='InvoiceBilling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date')),
                ('updated_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date')),
                ('pay_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Payable Amount')),
                ('payed_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Payed Amount')),
                ('payment_status', models.BooleanField(choices=[(False, 'Pending'), (True, 'Payed')], default=False, verbose_name='Payment Received')),
                ('pay_method', models.CharField(choices=[('0', 'PayPalAccount'), ('1', 'CreditCard')], default='0', max_length=5, verbose_name='Payment Method')),
                ('pay_mnth', models.CharField(max_length=2, verbose_name='Pay Month')),
                ('pay_yr', models.CharField(max_length=4, verbose_name='Pay Year')),
                ('transaction_id', models.CharField(blank=True, max_length=500, null=True, verbose_name='Transaction id')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices_billing', to='invoices.Invoice', verbose_name='Invoice Vault')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by')),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='billing_user', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Billing Info',
                'verbose_name_plural': 'Billing Info',
            },
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
        migrations.AddField(
            model_name='businesslogoinvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='businesslogoinvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='embedinvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='embedinvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='plugininvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='plugininvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='postinvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='postinvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='shareinvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='shareinvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='visitcharges',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='visitcharges',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AddField(
            model_name='weblinkinvoice',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='weblinkinvoice',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='updated by'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='business_logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='BusinessLogo', to='user.BusinessLogo'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='logo_count',
            field=models.IntegerField(default=0, verbose_name='Logo PPV Count'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='logo_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='logo_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='logo_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logo_viewer_user', to=settings.AUTH_USER_MODEL, verbose_name='Business Logo User'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='total_logo_count',
            field=models.IntegerField(default=0, verbose_name='Total Count (PPV)'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_logo_user', to=settings.AUTH_USER_MODEL, verbose_name='Business Logo Visitor'),
        ),
        migrations.AlterField(
            model_name='businesslogoinvoice',
            name='user_total_due',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='embed_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Embed Count'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='embed_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='embed_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='embed_total_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Total Count'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='skigit_embed_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='skigit_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skigit_embed_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit User'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='embedinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='embed_business_user', to=settings.AUTH_USER_MODEL, verbose_name='Business User'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='current_plugin_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plug_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plugin_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='Plugin Count'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plugin_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ski', to='skigit.VideoDetail', verbose_name='Plugged Skigit'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plugin_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='plugin_total_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='Total Count'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='primary_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plug_ski', to='skigit.VideoDetail', verbose_name='Skigit'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='skigit_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='skigit_plugin_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit Logo User'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='plugininvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_plugin_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='logo_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b_logo_user', to=settings.AUTH_USER_MODEL, verbose_name='Logo User'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Post Count'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_ski',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='skigit.VideoDetail'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='post_total_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Total Count'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='skigit_post_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='social_network_type',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Social Network Type'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='postinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_post_user', to=settings.AUTH_USER_MODEL, verbose_name='Post User'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='share_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Share Count'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='share_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='share_total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='skigit_share_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='skigit_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skigit_share_user', to=settings.AUTH_USER_MODEL, verbose_name='Skigit User'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='total_share_count',
            field=models.IntegerField(blank=True, null=True, verbose_name='Total Count'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='shareinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_share_user', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='embed_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=49.0, max_digits=9, verbose_name='Embed Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='link_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=1.99, max_digits=9, verbose_name='Web Link Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='logo_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.29, max_digits=9, verbose_name='Logo PPV Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='plug_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.29, max_digits=9, verbose_name='Plugin Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='post_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.79, max_digits=9, verbose_name='Post Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='share_charge',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.49, max_digits=9, verbose_name='Share Charge'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='visitcharges',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='superuse_payment', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_date'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='link_count',
            field=models.IntegerField(default=0, verbose_name='Links Count'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='link_due_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='link_is_paid',
            field=models.BooleanField(default=False, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='link_total_count',
            field=models.IntegerField(default=0, verbose_name='Total Count'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='link_total_due',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=9, verbose_name='Total Due Amount($)'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='updated_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated_date'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='link_visitor_user', to=settings.AUTH_USER_MODEL, verbose_name='Business User'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='web_link',
            field=models.URLField(blank=True, null=True, verbose_name='Awesome Company Links'),
        ),
        migrations.AlterField(
            model_name='weblinkinvoice',
            name='web_link_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='web_link_user', to=settings.AUTH_USER_MODEL, verbose_name='Web Link User'),
        ),
    ]