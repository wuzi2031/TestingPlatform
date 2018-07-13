from django.db import models
from case.models import TestTask
from datetime import datetime
from device.models import Device


# Create your models here.
class TestDataConfig(models.Model):
    """
    测试数据配置
    """
    TYPE = (
        ("test", "测试环境"),
        ("gld", "灰度环境"),
        ("pro", "生产环境")
    )
    name = models.CharField(max_length=30, verbose_name="名称")
    type = models.CharField(max_length=30, choices=TYPE, verbose_name="类型")
    web_url = models.CharField(max_length=100, verbose_name="web域名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "测试数据配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DataBaseConfig(models.Model):
    """
    数据库
    """
    test_data_config = models.ForeignKey(TestDataConfig, related_name="data_bases", verbose_name="测试数据配置")
    name = models.CharField(max_length=30, verbose_name="名称")
    database_host = models.CharField(max_length=100, verbose_name="数据库链接")
    database_port = models.CharField(max_length=10, verbose_name="数据库端口")
    database_user = models.CharField(max_length=100, verbose_name="数据库用户名")
    database_password = models.CharField(max_length=100, verbose_name="数据库密码")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "数据库配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class EnvConfig(models.Model):
    TYPE = (
        ("appium", "Appimu"),
        ("robotium", "robotium")
    )
    task = models.ForeignKey(TestTask, related_name='env', verbose_name='测试任务')
    app = models.FileField(blank=True, null=True, upload_to='app/', verbose_name="被测应用")
    test_app = models.FileField(blank=True, null=True, upload_to='app/', verbose_name="测试应用")
    app_script_type = models.CharField(max_length=30, choices=TYPE, verbose_name="类型")
    is_scene_test = models.BooleanField(default=False, verbose_name="是否场景测试")
    data_config = models.ForeignKey(TestDataConfig, blank=True, null=True, verbose_name="测试数据配置")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "执行环境配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.task.name


class DeviceRelateEnv(models.Model):
    env = models.ForeignKey(EnvConfig, related_name="relate_device", verbose_name="环境")
    device = models.ForeignKey(Device, verbose_name="设备")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "设备关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device.name
