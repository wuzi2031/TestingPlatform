from rest_framework import mixins, viewsets
from .models import Product, ModuleCategory, CaseSet
from .serializers import ProductSerializer, ModuleCategorySerializer, CaseSetSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ModuleCategoryFilter


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ModuleCategoryViewSet(viewsets.ModelViewSet):
    queryset = ModuleCategory.objects.all()
    serializer_class = ModuleCategorySerializer
    # permission_classes = (IsAuthenticated,)  # 登录验证
    # authentication_classes = (JSONWebTokenAuthentication,)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter)  # 排序过滤
    filter_class = ModuleCategoryFilter
    ordering_fields = ('add_time',)  # 排序字段


class CaseSetViewSet(viewsets.ModelViewSet):
    queryset = CaseSet.objects.all()
    serializer_class = CaseSetSerializer
    # permission_classes = (IsAuthenticated,)  # 登录验证
    # authentication_classes = (JSONWebTokenAuthentication,)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)  # 搜索排序过滤
    filter_fields = ('module',)
    search_fields = ('name',)  # 搜索字段
    ordering_fields = ('add_time',)  # 排序字段
