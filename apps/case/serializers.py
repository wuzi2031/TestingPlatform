from rest_framework import serializers
from .models import Product, ModuleCategory, Case, CaseScript, ScriptExcConfig, CaseSet
from datetime import datetime


class ProductSerializer(serializers.ModelSerializer):
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
        fields = ("id", "name", "code", "product_type", "package_name", "desc", "add_time")


class ModuleCategorySerializer(serializers.ModelSerializer):
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
