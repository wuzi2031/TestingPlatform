# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-09 15:02
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0011_auto_20180731_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 9, 15, 2, 5, 699341), verbose_name='修改时间'),
        ),
        migrations.AlterField(
            model_name='casescript',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 9, 15, 2, 5, 700751), verbose_name='修改时间'),
        ),
    ]
