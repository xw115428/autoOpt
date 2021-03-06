# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-06-08 09:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetsColum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name=b'\xe6\x9c\xba\xe6\x9f\x9c\xe5\x88\x97')),
            ],
            options={
                'verbose_name_plural': '\u673a\u67dc\u5217',
            },
        ),
        migrations.CreateModel(
            name='CabinetsNum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=16, null=True, verbose_name=b'\xe6\x9c\xba\xe6\x9f\x9c\xe5\x8f\xb7')),
                ('cabinet_num', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.CabinetsColum', verbose_name=b'\xe5\xb1\x9e\xe4\xba\x8e\xe5\x93\xaa\xe4\xb8\x80\xe6\x8e\x92\xe6\x9c\xba\xe6\x9f\x9c')),
            ],
            options={
                'verbose_name_plural': '\u673a\u67dc\u53f7',
            },
        ),
        migrations.CreateModel(
            name='ChildrenSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name=b'\xe5\xad\x90\xe7\xb3\xbb\xe7\xbb\x9f')),
                ('business_unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.BusinessUnit', verbose_name=b'\xe5\xb1\x9e\xe4\xba\x8e\xe5\x93\xaa\xe4\xb8\x80\xe4\xb8\xaa\xe4\xb8\x9a\xe5\x8a\xa1\xe7\xba\xbf')),
            ],
            options={
                'verbose_name_plural': '\u5b50\u7cfb\u7edf\u8868',
            },
        ),
        migrations.AlterModelOptions(
            name='asset',
            options={'verbose_name_plural': '\u901a\u7528\u4fe1\u606f\u8868'},
        ),
        migrations.RemoveField(
            model_name='asset',
            name='cabinet_num',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='cabinets_column',
        ),
        migrations.AddField(
            model_name='server',
            name='cpu_amount',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'CPU\xe6\x95\xb0\xe9\x87\x8f'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='buy_date',
            field=models.DateField(blank=True, default=datetime.datetime(2017, 11, 1, 0, 0), null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='cabinet_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.CabinetsNum', verbose_name=b'\xe5\xb1\x9e\xe4\xba\x8e\xe5\x93\xaa\xe4\xb8\x80\xe4\xb8\xaa\xe6\x9c\xba\xe6\x9f\x9c'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='guarantee_time',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name=b'\xe8\xb4\xa8\xe4\xbf\x9d\xe6\x9c\x9f'),
        ),
        migrations.AlterField(
            model_name='hostgroup',
            name='name',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name=b'\xe7\xbb\x84\xe5\x90\x8d\xe7\xa7\xb0'),
        ),
        migrations.AlterField(
            model_name='server',
            name='cpu_count',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'CPU\xe6\x80\xbb\xe6\xa0\xb8\xe6\x95\xb0'),
        ),
        migrations.AlterField(
            model_name='server',
            name='hostgroup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.HostGroup', verbose_name=b'\xe5\xb1\x9e\xe4\xba\x8e\xe7\x9a\x84\xe4\xb8\xbb\xe6\x9c\xba\xe7\xbb\x84'),
        ),
        migrations.AddField(
            model_name='server',
            name='children_system',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.ChildrenSystem', verbose_name=b'\xe5\xb1\x9e\xe4\xba\x8e\xe5\x93\xaa\xe4\xb8\x80\xe5\xad\x90\xe7\xb3\xbb\xe7\xbb\x9f'),
        ),
    ]
