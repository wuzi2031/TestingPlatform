from datetime import datetime

from django.db import models

from case.models import TestTask
from dataconfig.models import TestDataConfig
from device.models import Device


# Create your models here.

class EnvConfig(models.Model):
    TYPE = (
        ("appium", "Appimu"),
        ("robotium", "robotium")
    )
    task = models.ForeignKey(TestTask, related_name='env', verbose_name='测试任务')
    is_scene_test = models.BooleanField(default=False, verbose_name='是否场景测试')
    app_script_type = models.CharField(max_length=30, choices=TYPE, verbose_name="类型")
    data_config = models.ForeignKey(TestDataConfig, blank=True, null=True, verbose_name="测试数据配置")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "执行环境配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.task.name


class ApKConfig(models.Model):
    name = models.CharField(default="", max_length=30, verbose_name="名称", help_text="名称")
    env = models.ForeignKey(EnvConfig, related_name="relate_apks", verbose_name="环境")
    app = models.FileField(upload_to='app/', verbose_name="被测应用")
    package_name = models.CharField(max_length=200, null=True, blank=True, help_text="apk包名", verbose_name='包名')
    package_start_activity = models.CharField(max_length=200, null=True, blank=True, help_text="apk启动页",
                                              verbose_name='apk启动页')
    test_app = models.FileField(blank=True, null=True, upload_to='app/', verbose_name="测试应用")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "执行环境配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class DeviceRelateApK(models.Model):
    apKConfig = models.ForeignKey(ApKConfig, related_name="relate_device", verbose_name="apk")
    device = models.ForeignKey(Device, verbose_name="设备")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "设备关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.device.name


class RemoteService(models.Model):
    """
    远程服务数据记录
    """
    TYPE = (
        ("appium", "Appimu"),
        ("selenium", "Selenium")
    )
    env_config = models.ForeignKey(EnvConfig, related_name="remote_service", verbose_name="测试数据配置")
    keyword = models.CharField(null=True, blank=True, max_length=30, verbose_name="关键字")
    type = models.CharField(max_length=30, choices=TYPE, verbose_name="类型")
    host = models.CharField(max_length=30, verbose_name="ip")
    port = models.CharField(max_length=10, verbose_name='端口号')
    device_name = models.CharField(max_length=10, null=True, blank=True, verbose_name="设备mode名称")
    device_code = models.CharField(max_length=10, null=True, blank=True, verbose_name="设备device_id")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "url数据配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.env_config.task.name
