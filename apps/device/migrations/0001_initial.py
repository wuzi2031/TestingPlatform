# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-16 16:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', help_text='设备名', max_length=30, verbose_name='设备名')),
                ('code', models.CharField(default='', help_text='设备code', max_length=30, verbose_name='设备code')),
                ('version', models.CharField(default='', help_text='设备版本', max_length=30, verbose_name='设备版本')),
                ('env_type', models.CharField(help_text='如:android_mobile,android_pos,computer...', max_length=200, verbose_name='产品型号')),
                ('desc', models.TextField(default='', help_text='描述', verbose_name='产品描述')),
                ('device_type', models.CharField(choices=[('android', '安卓设备'), ('ios', 'ios设备'), ('pc', '电脑'), ('network', '网络设备'), ('other', '其他')], default='android', max_length=20, verbose_name='设备类型')),
                ('state', models.CharField(choices=[('online', '在线'), ('offline', '离线'), ('other', '其他')], default='offline', max_length=20, verbose_name='在线状态')),
                ('source', models.CharField(max_length=20, verbose_name='来源（执行机）')),
                ('is_used', models.BooleanField(default=False, verbose_name='是否被占用')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
            ],
            options={
                'verbose_name': '设备',
                'verbose_name_plural': '设备',
            },
        ),
    ]
