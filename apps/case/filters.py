import django_filters
from django.db.models import Q  # 这个Q可以支持表查询，单下划线获取表字段，双下划线获取关联表，

from .models import Case
from .models import ModuleCategory


# 自定义的过滤类，需要继承django_filter.rest_framework中的FilterSet类
class ModuleCategoryFilter(django_filters.rest_framework.FilterSet):
    # module_id = django_filters.NumberFilter(method='category_filter', label='module_id')
    product_id = django_filters.NumberFilter(method='product_filter', label='product_id')

    # django_filters.NumberFilter类似，ModelForm中字段类型的控制
    # 其中method指向自己定义的过滤函数，label用于标识在测试API界面中的过滤界面字段，module_id控制查询字段
    def category_filter(self, queryset, name, value):
        # 这里用到多级联表查询
        return queryset.filter(
            Q(id=value) | Q(parent_category=value) | Q(parent_category__parent_category=value) | Q(
                parent_category__parent_category__parent_category=value))

    def product_filter(self, queryset, name, value):
        return queryset.filter(Q(product__id=value))

    class Meta:
        model = ModuleCategory
        fields = ['product_id', ]


class CaseListFilter(django_filters.rest_framework.FilterSet):
    product = django_filters.NumberFilter(field_name="product", label='产品')
    module = django_filters.NumberFilter(field_name="module", label='模块')
    case_type = django_filters.ChoiceFilter(choices=Case.CASE_TYPE, label='用例类型')
    title = django_filters.CharFilter(method='title_filter', label='用例标题')
    test_type = django_filters.CharFilter(method='test_type_filter', label='测试类型')

    def title_filter(self, queryset, name, value):
        return queryset.filter(title__contains=value)

    def test_type_filter(self, queryset, name, value):
        return queryset.filter(test_type__contains=value)

    class Meta:
        model = Case
        fields = ['product', 'module', 'case_type']
