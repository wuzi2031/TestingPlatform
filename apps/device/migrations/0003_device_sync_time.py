# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-27 16:05
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0002_auto_20180721_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='sync_time',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='同步时间'),
        ),
    ]
