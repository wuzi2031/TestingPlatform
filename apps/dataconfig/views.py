from rest_framework import mixins, viewsets
from .models import TestDataConfig, DataBaseConfig
from .serializers import TestDataConfigSerializer, \
    DataBaseConfigSerializer

from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataConfigViewSet(viewsets.ModelViewSet):
    """
    测试数据配置
    """
    queryset = TestDataConfig.objects.all()
    serializer_class = TestDataConfigSerializer


class DataBaseConfigViewSet(viewsets.ModelViewSet):
    """
    数据库配置
    """
    queryset = DataBaseConfig.objects.all()
    serializer_class = DataBaseConfigSerializer
