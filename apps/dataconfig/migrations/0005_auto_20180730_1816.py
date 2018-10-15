# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-30 18:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataconfig', '0004_auto_20180730_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='databaseconfig',
            name='test_data_config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_bases', to='dataconfig.TestDataConfig', verbose_name='环境数据配置'),
        ),
        migrations.AlterField(
            model_name='urldataconfig',
            name='test_data_config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='dataconfig.TestDataConfig', verbose_name='环境数据配置'),
        ),
    ]
