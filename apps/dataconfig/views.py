from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import TestDataConfig, DataBaseConfig, UrlDataConfig
from .serializers import TestDataConfigSerializer, DataBaseConfigSerializer, UrlDataConfigSerializer

User = get_user_model()


class TestDataConfigViewSet(viewsets.ModelViewSet):
    """
    环境数据配置
    """
    queryset = TestDataConfig.objects.all()
    serializer_class = TestDataConfigSerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


class UrlDataConfigViewSet(viewsets.ModelViewSet):
    """
    url数据配置
    """
    queryset = UrlDataConfig.objects.all()
    serializer_class = UrlDataConfigSerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


class DataBaseConfigViewSet(viewsets.ModelViewSet):
    """
    数据库配置
    """
    queryset = DataBaseConfig.objects.all()
    serializer_class = DataBaseConfigSerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
