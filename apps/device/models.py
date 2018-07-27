from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class Device(models.Model):
    """
    设备
    """
    DEVICE_TYPE = (
        ("android_mobile", "安卓手机"),
        ("android_pos", "安卓POS"),
        ("android_pad", "安卓PAD"),
        ("ios", "ios设备"),
        ("pc", "电脑"),
        ("network", "网络设备"),
        ("other", "其他")
    )
    STATE = (
        ("online", "在线"),
        ("offline", "离线"),
        ("other", "其他")
    )

    name = models.CharField(default="", max_length=30, verbose_name="设备名", help_text="设备名")
    code = models.CharField(default="", max_length=30, verbose_name="设备code", help_text="设备code")
    version = models.CharField(default="", max_length=30, verbose_name="设备版本", help_text="设备版本")
    desc = models.TextField(default="", verbose_name="产品描述", help_text="描述")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE, default="android", verbose_name="设备类型")
    state = models.CharField(max_length=20, choices=STATE, default="offline", verbose_name="在线状态")
    source = models.CharField(max_length=20, verbose_name="来源（执行机）")
    is_used = models.BooleanField(default=False, verbose_name="是否被占用")
    sync_time = models.DateTimeField(default=datetime.now, verbose_name="同步时间")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
