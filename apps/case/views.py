from rest_framework import mixins, viewsets
from .models import Product, ModuleCategory
from .serializers import ProductSerializer, ModuleCategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
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
    filter_backends = (DjangoFilterBackend,)  # 搜索排序过滤
    filter_fields = ('product',)
    filter_class = ModuleCategoryFilter
    ordering_fields = ('add_time')  # 排序字段

    # def get_queryset(self):
    #     user = self.request.user
    #     return ModuleCategory.objects.filter(user=user)
        # query_params_dict = self.request.query_params
        # product_id = query_params_dict['product']
        # parent_category = query_params_dict['parent_category']
        # if (not product_id and not parent_category):
        #     return self.queryset
        # else:
        #     if product_id:
        #         product = Product.objects.filter(id=product_id)
        #         ModuleCategory.objects.filter(product=product)
