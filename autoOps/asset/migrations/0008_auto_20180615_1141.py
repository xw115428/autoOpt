# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-06-15 11:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0007_auto_20180609_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskjob',
            name='exec_result',
            field=models.CharField(blank=True, default=b'\xe6\x89\xa7\xe8\xa1\x8c\xe5\xae\x8c\xe6\xaf\x95', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='cabinet_order',
            field=models.IntegerField(blank=True, max_length=32, null=True, verbose_name=b'\xe6\x9c\xba\xe6\x9f\x9c\xe4\xb8\xad\xe7\x9a\x84\xe5\xba\x8f\xe5\x8f\xb7'),
        ),
    ]
