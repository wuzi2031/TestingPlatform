from datetime import datetime

from rest_framework import serializers

from dataconfig.serializers import TestDataConfig, TestDataConfigSerializer
from device.models import Device
from utils.common import getApkInfo
from .models import EnvConfig, DeviceRelateApK, ApKConfig


class ApKConfigSerializer(serializers.ModelSerializer):
    """
    apk配置
    """
    name = serializers.CharField(read_only=True)
    app = serializers.FileField()
    package_name = serializers.CharField(read_only=True)
    package_start_activity = serializers.CharField(read_only=True)
    test_app = serializers.FileField(allow_null=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def create(self, validated_data):
        instance = ApKConfig.objects.create(**validated_data)
        app_path = instance.app.path
        info = getApkInfo(app_path)
        instance.name = info[0]
        instance.package_name = info[1]
        instance.package_start_activity = info[2]
        instance.save()
        return instance

    class Meta:
        model = ApKConfig
        fields = "__all__"


class EnvConfigSerializer(serializers.ModelSerializer):
    """
    任务环境
    """
    data_config_id = serializers.CharField(write_only=True, help_text="数据配置id")
    # app = serializers.FileField(allow_null=True)
    # test_app = serializers.FileField(allow_null=True)
    data_config = TestDataConfigSerializer(read_only=True, help_text="数据配置")
    # devices = serializers.SerializerMethodField(read_only=True, help_text="设备列表")
    relate_apks = ApKConfigSerializer(many=True, read_only=True, help_text='apk配置')
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    # def get_devices(self, obj):
    #     return DeviceRelateEnv.objects.filter(env=obj)

    def validate(self, attrs):
        data_config_id = self.initial_data['data_config_id']
        data_confs = TestDataConfig.objects.filter(id=data_config_id)
        if (data_confs.count() == 0):
            raise serializers.ValidationError("数据配置不存在")
        attrs['data_config'] = data_confs[0]
        del attrs['data_config_id']
        self.fields.pop('data_config_id')
        return attrs

    class Meta:
        model = EnvConfig
        fields = "__all__"


class DeviceRelateApKSerializer(serializers.ModelSerializer):
    """
    设备数据
    """
    # device = DeviceSerializer(read_only=True, many=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        device_id = self.initial_data['device']
        device = Device.objects.filter(id=device_id)
        if not (device.state == "online" or device.is_used == False):
            raise serializers.ValidationError("请选择在线的空闲设备")
        return attrs

    def create(self, validated_data):
        instance = DeviceRelateApK.objects.create(**validated_data)
        device = instance.device
        device.is_used = True
        device.save()
        return instance

    class Meta:
        model = DeviceRelateApK
        fields = "__all__"
