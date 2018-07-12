# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-06-28 14:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0013_auto_20180621_1143'),
    ]

    operations = [
        migrations.CreateModel(
            name='group_onemenu_permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('onemenu_name', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'verbose_name_plural': '\u4e00\u7ea7\u83dc\u5355\u6743\u9650',
            },
        ),
        migrations.CreateModel(
            name='group_threebutton_permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threebutton_name', models.CharField(blank=True, max_length=64, null=True)),
                ('threebutton_url', models.CharField(blank=True, max_length=16, null=True)),
                ('threebutton', models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='group_twomenu_permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twomenu_name', models.CharField(blank=True, max_length=128, null=True)),
                ('twomenu_url', models.CharField(blank=True, max_length=256, null=True)),
                ('group_onemenu_permission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.group_onemenu_permission')),
            ],
            options={
                'verbose_name_plural': '\u4e8c\u7ea7\u83dc\u5355\u6743\u9650',
            },
        ),
        migrations.CreateModel(
            name='user_group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=64, null=True)),
                ('group_member', models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '\u7528\u6237\u7ec4\u8868',
            },
        ),
        migrations.AddField(
            model_name='group_onemenu_permission',
            name='user_group',
            field=models.ManyToManyField(blank=True, null=True, to='asset.user_group'),
        ),
    ]