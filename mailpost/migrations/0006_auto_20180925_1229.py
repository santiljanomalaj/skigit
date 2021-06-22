# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-25 12:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailpost', '0005_auto_20180925_1221'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailBody',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('to_email', models.CharField(blank=True, max_length=255, null=True)),
                ('from_email', models.CharField(blank=True, max_length=255, null=True)),
                ('html_template', models.TextField(blank=True, null=True)),
                ('is_html', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('template_key', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailFooter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_template', models.TextField(blank=True, null=True)),
                ('template_key', models.CharField(max_length=255, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html_template', models.TextField(blank=True, null=True)),
                ('template_key', models.CharField(max_length=255, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='EmailTemplate',
        ),
        migrations.DeleteModel(
            name='TemplateFooter',
        ),
        migrations.DeleteModel(
            name='TemplateHeader',
        ),
        migrations.AddField(
            model_name='emailbody',
            name='footer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailpost.EmailFooter'),
        ),
        migrations.AddField(
            model_name='emailbody',
            name='header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailpost.EmailHeader'),
        ),
    ]