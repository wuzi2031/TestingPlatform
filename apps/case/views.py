from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.mode import modelToJson
from .filters import ModuleCategoryFilter
from .models import Product, ModuleCategory, CaseSet, CaseReleteCaseSet, Case, TestTask, CaseReleteTestTask, CaseScript
from .serializers import ProductSerializer, ModuleCategorySerializer, CaseSetSerializer, \
    CaseReleteCaseSetSortUpdateSerializer, CaseReleteCaseSetSerializer, CaseSerializer, TestTaskSerialaer, \
    CaseReleteTestTaskSerializer, CaseReleteTestTaskSortUpdateSerializer, CaseScriptSerializer


class Pagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    产品
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


class ModuleCategoryViewSet(viewsets.ModelViewSet):
    """
    产品模块
    """
    queryset = ModuleCategory.objects.all()
    serializer_class = ModuleCategorySerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
    filter_backends = (DjangoFilterBackend,)  # 排序过滤
    filter_class = ModuleCategoryFilter

    # ordering_fields = ('add_time',)  # 排序字段

    def gen_children(self, children):
        for child in children:
            id = child.get('id')
            clist = self.children_dict.get(id)
            if clist:
                child['children'] = clist
                self.gen_children(clist)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        dataes = serializer.data
        self.children_dict = {}
        for data in dataes:
            data_dict = {}
            data_dict['id'] = data['id']
            data_dict['parent_category'] = data['parent_category']
            data_dict['product'] = data['product']['id']
            data_dict['name'] = data['name']
            data_dict['code'] = data['code']
            data_dict['desc'] = data['desc']
            parent_cat = data_dict.get('parent_category')
            if not parent_cat:
                parent_cat = 0
            key_exist = parent_cat in self.children_dict.keys()
            if key_exist:
                list = self.children_dict.get(parent_cat)
                list.append(data_dict)
            else:
                list = []
                list.append(data_dict)
                self.children_dict[parent_cat] = list
        child_list = self.children_dict.get(0)
        if child_list:
            self.gen_children(self.children_dict.get(0))
        else:
            child_list = []
        return Response(child_list)


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
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
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
            case_dict = modelToJson(case_re_set.case)
            case_dict['sort'] = case_re_set.sort
            case_list.append(case_dict)
        re_dict_case["cases"] = sorted(case_list, key=lambda case: case["sort"])
        return Response(re_dict_case)

    def sortCase(self, case_list):
        for case in case_list:
            return case['sort']


class CaseViewSet(viewsets.ModelViewSet):
    """
    用例
    list:
        用例列表，module过滤该模块下的用例
    create:
        创建用例
    update:
        修改用例
    destroy:
        删除用例
    retrieve:
        获取用例
    """
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)  # 搜索排序过滤
    filter_fields = ('module',)
    search_fields = ('title',)  # 搜索字段
    ordering_fields = ('add_time',)  # 排序字段


class CaseReleteCaseSetViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
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

    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_result = self.perform_create(serializer)
        re_dict_case = list()
        for case_re_set in list_result:
            re_dict = {}
            re_dict["id"] = case_re_set.id
            re_dict["sort"] = case_re_set.sort
            re_dict["case_set"] = case_re_set.case_set.id
            re_dict["case"] = modelToJson(case_re_set.case)
            re_dict_case.append(re_dict)
        # headers = self.get_success_headers(serializer.data)
        return Response(re_dict_case, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        list_result = serializer.save()
        return list_result


class CaseReleteCaseSetSortUpdateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    修改测试集序号
    """
    queryset = CaseReleteCaseSet.objects.all()
    serializer_class = CaseReleteCaseSetSortUpdateSerializer

    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_result = self.perform_create(serializer)
        re_dict_case = list()
        for case_re_set in list_result:
            re_dict = {}
            re_dict["id"] = case_re_set.id
            re_dict["sort"] = case_re_set.sort
            re_dict["case_set"] = case_re_set.case_set.id
            re_dict["case"] = case_re_set.case.id
            # re_dict["case"] = modelToJson(case_re_set.case)
            re_dict_case.append(re_dict)
        # headers = self.get_success_headers(serializer.data)
        return Response(re_dict_case, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        list_result = serializer.save()
        return list_result


class TestTaskViewSet(viewsets.ModelViewSet):
    """
    测试任务
    """
    queryset = TestTask.objects.filter(Q(task_state='not_start') | Q(task_state='executing'))
    serializer_class = TestTaskSerialaer

    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)  # 搜索排序过滤
    filter_fields = ('user',)
    search_fields = ('name',)  # 搜索字段
    ordering_fields = ('add_time',)  # 排序字段


class CaseReleteTestTaskViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    添加用例到测试任务
    list:
        任务下所有用例
    create:
        批量添加用例
    delete:
        删除单个用例
    """
    queryset = CaseReleteTestTask.objects.all()
    serializer_class = CaseReleteTestTaskSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)  # 搜索排序过滤
    filter_fields = ('test_task',)
    ordering_fields = ('add_time', 'sort')  # 排序字段

    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.perform_create(serializer)
        re_dict = modelToJson(task)
        # headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        task = serializer.save()
        return task

    def perform_destroy(self, instance):
        test_task = instance.test_task
        test_task.total_case_num -= 1
        test_task.save()
        instance.delete()


class CaseReleteTestTaskSortUpdateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    修改测试任务用例序号
    """
    queryset = CaseReleteTestTask.objects.all()
    serializer_class = CaseReleteTestTaskSortUpdateSerializer

    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        list_result = self.perform_create(serializer)
        re_dict_case = list()
        for case_re_task in list_result:
            re_dict = {}
            re_dict["id"] = case_re_task.id
            re_dict["sort"] = case_re_task.sort
            re_dict["test_task"] = case_re_task.test_task.id
            case_set = case_re_task.case_set
            if case_set:
                re_dict["case_set"] = case_set.id
            case = case_re_task.case
            if case:
                re_dict["case"] = case.id
            re_dict_case.append(re_dict)
        # headers = self.get_success_headers(serializer.data)
        return Response(re_dict_case, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        list_result = serializer.save()
        return list_result


class CaseScriptViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    脚本
    create:
        创建脚本(注意，关联到同一case的脚本要按执行的先后顺序添加)
    update:
        修改脚本
    destroy:
        删除脚本
    retrieve:
        获取脚本
    """
    queryset = CaseScript.objects.all()
    serializer_class = CaseScriptSerializer
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证
