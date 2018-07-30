from datetime import datetime

from rest_framework import serializers

from .models import TestDataConfig, DataBaseConfig, UrlDataConfig


class DataBaseConfigSerializer(serializers.ModelSerializer):
    """
    数据库配置
    """
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    class Meta:
        model = DataBaseConfig
        fields = "__all__"


class UrlDataConfigSerializer(serializers.ModelSerializer):
    """
    url配置
    """
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    class Meta:
        model = UrlDataConfig
        fields = "__all__"


class TestDataConfigSerializer(serializers.ModelSerializer):
    """
    环境数据配置
    """
    urls = UrlDataConfigSerializer(many=True, read_only=True, help_text='url数据')
    data_bases = DataBaseConfigSerializer(many=True, read_only=True, help_text="数据库")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    class Meta:
        model = TestDataConfig
        fields = "__all__"
