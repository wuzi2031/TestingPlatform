# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-06 10:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0023_auto_20180704_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 6, 10, 27, 33, 889626), verbose_name='修改时间'),
        ),
        migrations.AlterField(
            model_name='casescript',
            name='update_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 7, 6, 10, 27, 33, 891552), verbose_name='修改时间'),
        ),
    ]
