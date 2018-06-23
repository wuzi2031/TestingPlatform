from rest_framework import mixins, viewsets
from .models import Product, ModuleCategory, CaseSet, CaseReleteCaseSet
from .serializers import ProductSerializer, ModuleCategorySerializer, CaseSetSerializer
from .serializers import CaseReleteCaseSetSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import ModuleCategoryFilter
from rest_framework.response import Response
from rest_framework import status
from .utils import modelToJson


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    产品
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ModuleCategoryViewSet(viewsets.ModelViewSet):
    """
    产品模块
    """
    queryset = ModuleCategory.objects.all()
    serializer_class = ModuleCategorySerializer
    # permission_classes = (IsAuthenticated,)  # 登录验证
    # authentication_classes = (JSONWebTokenAuthentication,)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter)  # 排序过滤
    filter_class = ModuleCategoryFilter
    ordering_fields = ('add_time',)  # 排序字段


class CaseSetViewSet(viewsets.ModelViewSet):
    """
    测试集
    list:
        测试集列表，module过滤该模块下的测试集
    create:
        创建测试集
    update:
        修改测试集
    destroy:
        删除测试集
    retrieve:
        获取测试集和测试集下面的的用例
    """
    queryset = CaseSet.objects.all()
    serializer_class = CaseSetSerializer
    # permission_classes = (IsAuthenticated,)  # 登录验证
    # authentication_classes = (JSONWebTokenAuthentication,)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)  # 搜索排序过滤
    filter_fields = ('module',)
    search_fields = ('name',)  # 搜索字段
    ordering_fields = ('add_time',)  # 排序字段

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cases_re_set = CaseReleteCaseSet.objects.filter(case_set=instance)
        re_dict_case = modelToJson(instance)
        case_list = list()
        for case_re_set in cases_re_set:
            case_list.append(modelToJson(case_re_set.case))
        re_dict_case["cases"] = case_list
        return Response(re_dict_case)


class CaseReleteCaseSetSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
    用例与测试集关联
    create:
        批量关联测试用例
    delete:
        删除一条测试用例的关联
    """
    queryset = CaseReleteCaseSet.objects.all()
    serializer_class = CaseReleteCaseSetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_result = self.perform_create(serializer)
        re_dict_case = list()
        for case_re_set in list_result:
            re_dict = {}
            re_dict["id"] = case_re_set.id
            re_dict["case_set"] = case_re_set.case_set.id
            re_dict["case"] = modelToJson(case_re_set.case)
            re_dict_case.append(re_dict)
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict_case, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        list_result = serializer.save()
        return list_result
