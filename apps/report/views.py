from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from case.models import TestTask
from case.serializers import TestTaskSerialaer


# Create your views here.
class TaskReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    测试任务结果列表
    """
    queryset = TestTask.objects.filter(Q(task_state='block') | Q(task_state='finish') | Q(task_state='stop'))
    serializer_class = TestTaskSerialaer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('task_state',)
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
