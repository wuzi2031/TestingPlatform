from datetime import datetime

from rest_framework import serializers

from dataconfig.serializers import TestDataConfig, TestDataConfigSerializer
from device.models import Device
from utils.common import getApkInfo
from .models import EnvConfig, DeviceRelateApK, ApKConfig, WebConfig
from rest_framework.utils import model_meta

class WebConfigSerializer(serializers.ModelSerializer):
    """
    web配置
    """
    name = serializers.CharField(read_only=True)
    ready = serializers.BooleanField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        device_id = self.initial_data['device']

        devices = Device.objects.filter(id=device_id)
        if not devices:
            raise serializers.ValidationError("设备不存在")
        device = devices[0]
        env_id = self.initial_data['env']

        envs = EnvConfig.objects.filter(id=env_id)
        if not envs:
            raise serializers.ValidationError("环境不存在")
        env = envs[0]
        if not (device.state == "online" or not device.is_used):
            raise serializers.ValidationError("请选择在线的空闲设备")
        if not device.device_type == 'pc':
            raise serializers.ValidationError("请选择PC设备")
        wbs = WebConfig.objects.filter(device=device, env=env)
        if wbs and len(wbs) > 0:
            raise serializers.ValidationError("已添加过该设备")
        return attrs

    def create(self, validated_data):
        instance = WebConfig.objects.create(**validated_data)
        device = instance.device
        device.is_used = True
        device.save()
        instance.name = device.name
        instance.save()
        return instance

    class Meta:
        model = WebConfig
        fields = "__all__"


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

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)
        instance.save()
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
    relate_webs = WebConfigSerializer(many=True, read_only=True, help_text='web配置')
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
    ready = serializers.BooleanField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        device_id = self.initial_data['device']
        devices = Device.objects.filter(id=device_id)
        if not devices:
            raise serializers.ValidationError("设备不存在")
        device = devices[0]
        if not (device.state == "online" or not device.is_used):
            raise serializers.ValidationError("请选择在线的空闲设备")
        dbs = DeviceRelateApK.objects.filter(device=device)
        if dbs and len(dbs) > 0:
            raise serializers.ValidationError("已添加过该设备")
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
