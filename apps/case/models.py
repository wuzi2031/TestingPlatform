from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# Create your models here.
class Product(models.Model):
    """
    产品类别
    """

    name = models.CharField(default="", max_length=30, verbose_name="产品名", help_text="产品名")
    code = models.CharField(default="", max_length=30, verbose_name="产品code", help_text="产品code")
    desc = models.TextField(default="", verbose_name="产品描述", help_text="产品描述")
    # product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE, default="android_mobile", verbose_name="产品类型")
    # parent_category = models.ForeignKey("self", related_name="sub_product_cat", null=True, blank=True,
    #                                     verbose_name="父类目",
    #                                     help_text="父类目")
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='创建人')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "产品"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ModuleCategory(models.Model):
    """
    模块
    """
    product = models.ForeignKey(Product, verbose_name='产品')
    name = models.CharField(default="", max_length=30, verbose_name="模块名", help_text="模块名")
    code = models.CharField(default="", max_length=30, verbose_name="模块code", help_text="模块code")
    desc = models.TextField(default="", verbose_name="模块描述", help_text="模块描述")
    parent_category = models.ForeignKey("self", related_name="sub_module_cat", null=True, blank=True,
                                        verbose_name="父类目",
                                        help_text="父类目")
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='创建人')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "模块"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CaseSet(models.Model):
    """
    测试用例集
    """
    module = models.ForeignKey(ModuleCategory, related_name="caseset", verbose_name="产品模块")
    name = models.CharField(default="", max_length=30, verbose_name="用例集名", help_text="用例集名")
    desc = models.TextField(default="", verbose_name="用例集描述", help_text="用例集描述")
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='创建人')
    # is_del = models.BooleanField(default=False, verbose_name='是否已删除')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用例集"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Case(models.Model):
    """
    测试用例
    """
    CASE_TYPE = (
        ("functional", "功能测试"),
        ("performance", "性能测试"),
        ("api", "接口测试"),
        ("safe", "安全测试"),
        ("other", "其他")
    )

    product = models.ForeignKey(Product, related_name="case", verbose_name="产品")
    module = models.ForeignKey(ModuleCategory, related_name="case", verbose_name="产品模块")
    title = models.CharField(max_length=30, null=False, blank=False, verbose_name="用例标题")
    user = models.ForeignKey(User, verbose_name='创建人')
    # update_user = models.ForeignKey(User,verbose_name='修改人')
    case_type = models.CharField(max_length=20, choices=CASE_TYPE, default="functional", verbose_name="用例类型")
    test_type = models.CharField(max_length=20, blank=True, null=False, help_text="如：冒烟测试，场景测试等类型", verbose_name="测试类型")
    test_precondition = models.TextField(blank=True, null=True, verbose_name='前置条件')
    test_step = models.TextField(blank=True, null=True, verbose_name='测试步骤')
    enclosure_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='附件标题')
    enclosure = models.FileField(upload_to="case/enclosure", null=True, blank=True, verbose_name='用例附件')
    # is_del = models.BooleanField(default=False, verbose_name='是否已删除')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(default=datetime.now(), verbose_name="修改时间")

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class CaseReleteCaseSet(models.Model):
    """
    用例与测试集关联
    """
    case_set = models.ForeignKey(CaseSet, related_name="case", verbose_name="用例集")
    case = models.ForeignKey(Case, verbose_name='测试用例')
    sort = models.IntegerField(default=0, verbose_name="序号")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用例与测试集关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.case.title


class CaseScript(models.Model):
    """
    用例脚本
    """
    case = models.ForeignKey(Case, related_name='case_script', verbose_name='测试用例')
    name = models.CharField(max_length=50, verbose_name="脚本名称")
    prefix_path = models.CharField(max_length=200, null=True, blank=True, verbose_name='脚本执行前缀路径')
    script_file = models.FileField(blank=True, null=True, upload_to='case/script', verbose_name="脚本文件")
    upload_file = models.BooleanField(default=False, verbose_name="是否上传文件")
    # execute_env = models.CharField(max_length=200, blank=True, null=True, verbose_name="执行环境",
    #                                help_text="产品型号如:android_mobile,android_pos,computer...")
    desc = models.TextField(null=True, blank=True, verbose_name='描述')
    # is_del = models.BooleanField(default=False, verbose_name='是否已删除')
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='创建人')
    update_time = models.DateTimeField(default=datetime.now(), verbose_name="修改时间")

    class Meta:
        verbose_name = "用例脚本"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.case.title


class TestTask(models.Model):
    """
    测试任务
    """
    TASK_STATE = (
        ("not_start", "未开始"),
        ("executing", "执行中"),
        ("block", "执行中断"),
        ("finish", "执行完成"),
        ("stop", "执行停止")
    )
    name = models.CharField(max_length=50, verbose_name="任务名称")
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='创建人')
    task_state = models.CharField(max_length=20, choices=TASK_STATE, default="not_start", verbose_name="任务状态")
    total_case_num = models.IntegerField(null=True, blank=True, verbose_name="总用例数")
    success_case_num = models.IntegerField(null=True, blank=True, verbose_name="成功用例数")
    fail_case_num = models.IntegerField(null=True, blank=True, verbose_name="失败用例数")
    block_case_num = models.IntegerField(null=True, blank=True, verbose_name="阻塞用例数")
    re_execut_num = models.IntegerField(null=True, blank=True, verbose_name="失败重跑次数")
    desc = models.TextField(default="", verbose_name="描述", help_text="描述")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    execut_start_time = models.DateTimeField(null=True, blank=True, verbose_name="执行开始时间")
    execut_end_time = models.DateTimeField(null=True, blank=True, verbose_name="执行结束时间")
    execut_user = models.ForeignKey(User, related_name="user_testTask", null=True, blank=True, verbose_name='执行人')

    class Meta:
        verbose_name = "测试任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CaseReleteTestTask(models.Model):
    """
    用例与测试任务关联
    """
    test_task = models.ForeignKey(TestTask, related_name="case", verbose_name='测试任务')
    case = models.ForeignKey(Case, null=True, blank=True, verbose_name='用例')
    case_set = models.ForeignKey(CaseSet, null=True, blank=True, verbose_name='用例集')
    sort = models.IntegerField(default=0, verbose_name="序号")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用例与测试任务关联"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.test_task.name
