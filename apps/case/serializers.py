from rest_framework import serializers
from .models import Product, ModuleCategory, Case, CaseScript, CaseSet, CaseReleteCaseSet
from datetime import datetime
from django.db import transaction


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField()
    code = serializers.CharField()
    product_type = serializers.CharField(help_text="""
    ("mobile", "手机端应用"),
        ("web", "网页"),
        ("network", "网络设备"),
        ("other", "其他")
    """)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate_code(self, code):
        count = Product.objects.filter(code=code).count()
        if (count > 0):
            raise serializers.ValidationError("产品代码已存在")

    def validate_name(self, name):
        count = Product.objects.filter(name=name).count()
        if (count > 0):
            raise serializers.ValidationError("产品名称已存在")

    class Meta:
        model = Product
        fields = ("id", "user", "name", "code", "product_type", "package_name", "desc", "add_time")


class ModuleCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)
    product_id = serializers.CharField(help_text="产品id", write_only=True)
    name = serializers.CharField()
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        product_id = self.initial_data['product_id']
        code = self.initial_data['code']
        name = self.initial_data['name']
        product = Product.objects.filter(id=product_id)[0]
        count = ModuleCategory.objects.filter(code=code, product=product).count()
        if (count > 0):
            raise serializers.ValidationError("模块代码已存在")
        count = ModuleCategory.objects.filter(name=name, product=product).count()
        if (count > 0):
            raise serializers.ValidationError("模块名称已存在")
        attrs['product'] = product
        del attrs['product_id']
        self.fields.pop('product_id')
        return attrs

    class Meta:
        model = ModuleCategory
        fields = "__all__"


class CaseSetSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    module = ModuleCategorySerializer(read_only=True)
    module_id = serializers.CharField(help_text="模块id", write_only=True)
    name = serializers.CharField()
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        module_id = self.initial_data['module_id']
        name = self.initial_data['name']
        module = ModuleCategory.objects.filter(id=module_id)[0]

        count = CaseSet.objects.filter(name=name, module=module).count()
        if (count > 0):
            raise serializers.ValidationError("用例集名称已存在")
        attrs['module'] = module
        del attrs['module_id']
        self.fields.pop('module_id')
        return attrs

    class Meta:
        model = CaseSet
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = "__all__"


class CaseReleteCaseSetSerializer(serializers.ModelSerializer):
    case_id = serializers.ListField(help_text="用例id列表", write_only=True)
    case = CaseSerializer(read_only=True, many=True)
    case_set_id = serializers.IntegerField(help_text="测试集id", write_only=True)
    case_set = CaseSetSerializer(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        case_id = self.initial_data['case_id']
        case_set_id = self.initial_data['case_set_id']
        if not case_id:
            raise serializers.ValidationError("case_id不能为空")
        id_count = len(case_id)
        self.batch_case = Case.objects.filter(id__in=case_id)
        case_count = self.batch_case.count()
        if (id_count != case_count):
            raise serializers.ValidationError("用例id不存在")
        case_sets = CaseSet.objects.filter(id=case_set_id)
        if not case_sets:
            raise serializers.ValidationError("case_set_id不存在")
        self.case_set = case_sets[0]

        # attrs['case_set'] = case_set
        del attrs['case_id']
        del attrs['case_set_id']
        self.fields.pop('case_id')
        self.fields.pop('case_set_id')
        return attrs

    def create(self, validated_data):
        # batch_case_set = list()
        objs = list()
        with transaction.atomic():
            for case in self.batch_case:
                case_re_set = CaseReleteCaseSet()
                case_re_set.case_set = self.case_set
                case_re_set.case = case
                case_re_set.save()
                objs.append(case_re_set)
                # batch_case_set.append(re)
        # 批量创建不会返回主键
        # objs = CaseReleteCaseSet.objects.bulk_create(batch_case_set)
        return objs

    class Meta:
        model = CaseReleteCaseSet
        fields = "__all__"
