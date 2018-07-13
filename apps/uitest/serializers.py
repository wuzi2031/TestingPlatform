from rest_framework import serializers
from datetime import datetime
from .models import TestDataConfig, EnvConfig, DeviceRelateEnv, DataBaseConfig
from device.models import Device


class DataBaseConfigSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    class Meta:
        model = DataBaseConfig
        fields = "__all__"


class TestDataConfigSerializer(serializers.ModelSerializer):
    """
    测试数据配置
    """
    data_bases = DataBaseConfigSerializer(many=True, help_text="数据库")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    class Meta:
        model = TestDataConfig
        fields = "__all__"


class EnvConfigSerializer(serializers.ModelSerializer):
    """
    任务环境
    """
    data_config_id = serializers.CharField(write_only=True, help_text="数据配置id")
    app = serializers.FileField(allow_null=True)
    test_app = serializers.FileField(allow_null=True)
    data_config = TestDataConfigSerializer(read_only=True, help_text="数据配置")
    # devices = serializers.SerializerMethodField(read_only=True, help_text="设备列表")
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


class DeviceRelateEnvSerializer(serializers.ModelSerializer):
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
        instance = DeviceRelateEnv.objects.create(**validated_data)
        device = instance.device
        device.is_used = True
        device.save()
        return instance

    class Meta:
        model = DeviceRelateEnv
        fields = "__all__"
