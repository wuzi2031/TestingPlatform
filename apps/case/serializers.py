from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from .models import Product, ModuleCategory, Case, CaseScript, CaseSet, CaseReleteCaseSet, TestTask, CaseReleteTestTask


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField()
    code = serializers.CharField()
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate_code(self, code):
        count = Product.objects.filter(code=code).count()
        if (count > 0):
            raise serializers.ValidationError("产品代码已存在")
        return code

    def validate_name(self, name):
        count = Product.objects.filter(name=name).count()
        if (count > 0):
            raise serializers.ValidationError("产品名称已存在")
        return name

    class Meta:
        model = Product
        fields = ("id", "user", "name", "code", "desc", "add_time")


class ModuleCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = ProductSerializer(read_only=True)
    product_id = serializers.CharField(help_text="产品id", write_only=True)
    # name = serializers.CharField()
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
    module = serializers.SerializerMethodField()
    module_id = serializers.CharField(help_text="模块id", write_only=True)
    name = serializers.CharField()
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def get_module(self, obj):
        return obj.module.id

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


class CaseScriptSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    update_time = serializers.DateTimeField(read_only=True, default=datetime.now())

    class Meta:
        model = CaseScript
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    title = serializers.CharField(help_text="用例标题")
    case_type = serializers.CharField(help_text="""
    ("functional", "功能测试"),
        ("performance", "性能测试"),
        ("api", "接口测试"),
        ("safe", "安全测试"),
        ("other", "其他")
    """)
    test_type = serializers.CharField(required=False, help_text="自定义，如：冒烟测试，场景测试等类型")
    test_precondition = serializers.CharField(required=False, help_text="前置条件")
    test_step = serializers.CharField(required=False, help_text="测试步骤")
    enclosure_title = serializers.CharField(required=False, help_text="附件标题")
    enclosure = serializers.FileField(required=False, help_text="附件")
    add_time = serializers.DateTimeField(default=datetime.now, read_only=True)
    update_time = serializers.DateTimeField(default=datetime.now(), read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    case_script = CaseScriptSerializer(read_only=True, many=True)

    # module
    class Meta:
        model = Case
        fields = "__all__"


class CaseReleteCaseSetSerializer(serializers.ModelSerializer):
    case_id = serializers.ListField(help_text="用例id列表", write_only=True)
    sort_id = serializers.ListField(help_text="序号列表", write_only=True)
    case = CaseSerializer(read_only=True, many=True)
    case_set_id = serializers.IntegerField(help_text="测试集id", write_only=True)
    case_set = CaseSetSerializer(read_only=True)
    sort = serializers.IntegerField(read_only=True, help_text="排序序号")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        case_id = self.initial_data['case_id']
        case_set_id = self.initial_data['case_set_id']
        self.sort_id = self.initial_data['sort_id']
        if not self.sort_id:
            raise serializers.ValidationError("sort_id不能为空")
        if not case_id:
            raise serializers.ValidationError("case_id不能为空")
        id_count = len(case_id)
        if (id_count != len(self.sort_id)):
            raise serializers.ValidationError("case_id与sort_id长度不一致")
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
        del attrs['sort_id']
        self.fields.pop('case_id')
        self.fields.pop('case_set_id')
        self.fields.pop('sort_id')
        return attrs

    def create(self, validated_data):
        # batch_case_set = list()
        objs = list()
        with transaction.atomic():
            for case, i in zip(self.batch_case, self.sort_id):
                case_re_set = CaseReleteCaseSet()
                case_re_set.case_set = self.case_set
                case_re_set.case = case
                case_re_set.sort = i
                case_re_set.save()
                objs.append(case_re_set)
                # batch_case_set.append(re)
        # 批量创建不会返回主键
        # objs = CaseReleteCaseSet.objects.bulk_create(batch_case_set)
        return objs

    class Meta:
        model = CaseReleteCaseSet
        fields = "__all__"


class CaseReleteCaseSetSortUpdateSerializer(serializers.ModelSerializer):
    id_list = serializers.ListField(help_text="测试集关联id列表", write_only=True)
    sort_id = serializers.ListField(help_text="序号列表", write_only=True)
    case = serializers.SerializerMethodField()
    case_set = serializers.SerializerMethodField()
    sort = serializers.IntegerField(read_only=True, help_text="排序序号")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        self.sort_id = self.initial_data['sort_id']
        self.id_list = self.initial_data['id_list']
        if not self.id_list:
            raise serializers.ValidationError("id_list不能为空")
        if not self.sort_id:
            raise serializers.ValidationError("sort_id不能为空")

        if (len(self.id_list) != len(self.sort_id)):
            raise serializers.ValidationError("id_list与sort_id长度不一致")
        self.batch_case_re_set = CaseReleteCaseSet.objects.filter(id__in=self.id_list)
        count = self.batch_case_re_set.count()
        if (len(self.id_list) != count):
            raise serializers.ValidationError("测试集关联id不存在")

        del attrs['id_list']
        del attrs['sort_id']
        self.fields.pop('id_list')
        self.fields.pop('sort_id')
        return attrs

    def create(self, validated_data):
        # batch_case_set = list()
        objs = list()
        with transaction.atomic():
            for case_re_set, i in zip(self.batch_case_re_set, self.sort_id):
                case_re_set.sort = i
                case_re_set.save()
                objs.append(case_re_set)
                # batch_case_set.append(re)
        # 批量创建不会返回主键
        # objs = CaseReleteCaseSet.objects.bulk_create(batch_case_set)
        return objs

    class Meta:
        model = CaseReleteCaseSet
        fields = "__all__"


class TestTaskSerialaer(serializers.ModelSerializer):
    """
    测试任务
    """

    name = serializers.CharField(help_text="名称")
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    task_state = serializers.CharField(read_only=True, help_text="任务状态")
    total_case_num = serializers.IntegerField(read_only=True, help_text="用例总数")
    success_case_num = serializers.IntegerField(read_only=True, help_text="用例总数")
    fail_case_num = serializers.IntegerField(read_only=True, help_text="用例总数")
    block_case_num = serializers.IntegerField(read_only=True, help_text="用例总数")
    re_execut_num = serializers.IntegerField(read_only=True, help_text="用例总数")
    desc = serializers.CharField(allow_null=True, help_text="描述")
    add_time = serializers.DateTimeField(default=datetime.now, read_only=True, help_text="添加时间")
    execut_start_time = serializers.DateTimeField(read_only=True, help_text="执行开始时间")
    execut_end_time = serializers.DateTimeField(read_only=True, help_text="执行结束时间")
    execut_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TestTask
        fields = "__all__"


class CaseReleteTestTaskSerializer(serializers.ModelSerializer):
    test_task_id = serializers.IntegerField(help_text="任务id", write_only=True)
    case_id = serializers.ListField(allow_null=True, help_text="用例id列表", write_only=True)
    case_set_id = serializers.ListField(allow_null=True, help_text="测试集id", write_only=True)

    test_task = serializers.SerializerMethodField()
    case = CaseSerializer(read_only=True)
    case_set = CaseSetSerializer(read_only=True)
    sort = serializers.IntegerField(read_only=True, help_text="排序序号")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    # 如果是create被执行obj为seralizer的create方法返回的实例，否则一般为mate里面关联的mode实例
    def get_test_task(self, obj):
        if isinstance(obj, TestTask):
            return obj.id
        return obj.test_task.id

    def validate(self, attrs):
        test_task_id = self.initial_data['test_task_id']
        case_id = self.initial_data['case_id']
        case_set_id = self.initial_data['case_set_id']

        test_tasks = TestTask.objects.filter(id=test_task_id)
        if not test_tasks:
            raise serializers.ValidationError("test_task_id不存在")
        self.test_task = test_tasks[0]
        if not (case_id or case_set_id):
            raise serializers.ValidationError("case_id或者case_set_id其中一个不能为空")
        self.id_count = len(case_id)
        if self.id_count > 0:
            self.batch_case = Case.objects.filter(id__in=case_id)
            case_count = self.batch_case.count()
            if (self.id_count != case_count):
                raise serializers.ValidationError("用例id不存在")

        self.id_set_count = len(case_set_id)
        if self.id_set_count > 0:
            self.batch_caseset = CaseSet.objects.filter(id__in=case_set_id)
            caseset_count = self.batch_caseset.count()
            if (self.id_set_count != caseset_count):
                raise serializers.ValidationError("用例集id不存在")

        self.total_num = self.id_count + self.id_set_count
        # attrs['case_set'] = case_set
        del attrs['test_task_id']
        del attrs['case_id']
        del attrs['case_set_id']
        self.fields.pop('test_task_id')
        self.fields.pop('case_id')
        self.fields.pop('case_set_id')
        return attrs

    def create(self, validated_data):
        last_sort = 0;
        last = CaseReleteTestTask.objects.filter(test_task=self.test_task).last();
        if (last):
            last_sort = last.sort + 1
        batch_case_set = list()
        if self.id_count > 0:
            for case in self.batch_case:
                case_re_task = CaseReleteTestTask()
                case_re_task.test_task = self.test_task
                case_re_task.case = case
                case_re_task.sort = last_sort
                last_sort += 1
                batch_case_set.append(case_re_task)
        if self.id_set_count > 0:
            for caseset in self.batch_caseset:
                case_re_task = CaseReleteTestTask()
                case_re_task.test_task = self.test_task
                case_re_task.case_set = caseset
                case_re_task.sort = last_sort
                last_sort += 1
                batch_case_set.append(case_re_task)
        # 批量创建不会返回主键
        objs = CaseReleteTestTask.objects.bulk_create(batch_case_set)
        # 保存用例总数
        total = self.test_task.total_case_num
        if total:
            self.test_task.total_case_num = total + self.total_num
        else:
            self.test_task.total_case_num = self.total_num
        self.test_task.save()
        return self.test_task

    class Meta:
        model = CaseReleteTestTask
        fields = "__all__"


class CaseReleteTestTaskSortUpdateSerializer(serializers.ModelSerializer):
    """
    修改测试任务用例顺序
    """
    id_list = serializers.ListField(help_text="测试任务关联id列表", write_only=True)
    sort_id = serializers.ListField(help_text="序号列表", write_only=True)
    test_task = serializers.SerializerMethodField()
    case = serializers.SerializerMethodField()
    case_set = serializers.SerializerMethodField()
    sort = serializers.IntegerField(read_only=True, help_text="排序序号")
    add_time = serializers.DateTimeField(read_only=True, default=datetime.now)

    def validate(self, attrs):
        self.sort_id = self.initial_data['sort_id']
        self.id_list = self.initial_data['id_list']
        if not self.id_list:
            raise serializers.ValidationError("id_list不能为空")
        if not self.sort_id:
            raise serializers.ValidationError("sort_id不能为空")

        if (len(self.id_list) != len(self.sort_id)):
            raise serializers.ValidationError("id_list与sort_id长度不一致")
        self.batch_case_re_task = CaseReleteTestTask.objects.filter(id__in=self.id_list)
        count = self.batch_case_re_task.count()
        if (len(self.id_list) != count):
            raise serializers.ValidationError("测试集关联id不存在")

        del attrs['id_list']
        del attrs['sort_id']
        self.fields.pop('id_list')
        self.fields.pop('sort_id')
        return attrs

    def create(self, validated_data):
        # batch_case_set = list()
        objs = list()
        with transaction.atomic():
            for case_re_task, i in zip(self.batch_case_re_task, self.sort_id):
                case_re_task.sort = i
                case_re_task.save()
                objs.append(case_re_task)
                # batch_case_set.append(re)
        # 批量创建不会返回主键
        # objs = CaseReleteCaseSet.objects.bulk_create(batch_case_set)
        return objs

    class Meta:
        model = CaseReleteTestTask
        fields = "__all__"
