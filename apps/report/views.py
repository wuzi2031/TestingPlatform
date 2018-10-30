from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from case.models import TestTask
from case.serializers import TestTaskSerialaer
from .filters import TaskFilter, ReportCaseListFilter
from .models import TaskExecuteInfo
from .serializers import TaskExecuteInfoSerializer


class Pagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


# Create your views here.
class TaskReportViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    测试任务结果列表
    """
    queryset = TestTask.objects.filter(Q(task_state='block') | Q(task_state='finish') | Q(task_state='stop'))
    serializer_class = TestTaskSerialaer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = TaskFilter
    search_fields = ('name',)  # 搜索字段
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


# Create your views here.
class TaskExecuteInfoViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用例结果
    list:
        用例结果列表
    update:
        修改用例结果
    """
    queryset = TaskExecuteInfo.objects.all()
    serializer_class = TaskExecuteInfoSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)  # 搜索排序过滤
    filter_class = ReportCaseListFilter
    # search_fields = ('case__title',)  # 搜索字段
    ordering_fields = ('add_time',)  # 排序字段
