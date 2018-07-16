from rest_framework import serializers
from datetime import datetime
from .models import TestDataConfig, DataBaseConfig


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

