import xadmin
from .models import Product, ModuleCategory, Case, CaseScript, CaseSet, CaseReleteCaseSet, TestTask, CaseReleteTestTask


class ProductAdmin(object):
    list_display = ["name", "code", "desc", "product_type", "package_name", "add_time", "user"]
    search_fields = ['name', ]
    list_filter = ["name", "code", "desc", "product_type", "package_name", "add_time", "user"]


class ModuleCategoryAdmin(object):
    list_display = ["name", "product", "code", "desc", "parent_category", "add_time", "user"]
    list_filter = ["product", "parent_category", "name", "user"]
    search_fields = ['name', ]


class CaseAdmin(object):
    list_display = ["module", "title", "user", "case_type", "test_type", "test_precondition",
                    "test_step", "enclosure_title", "enclosure", "add_time", "update_time"]
    list_filter = ["title", "module", "case_type", "test_type", "user"]
    search_fields = ['title', ]


class CaseSetAdmin(object):
    list_display = ["module", "name", "user", "add_time"]
    list_filter = ["name", "module", "user", "add_time"]
    search_fields = ['name', ]

    class CaseReleteCaseSetInline(object):
        model = CaseReleteCaseSet
        exclude = ['add_time', ]
        extra = 1
        style = 'tab'

    inlines = [CaseReleteCaseSetInline, ]


class CaseScriptAdmin(object):
    list_display = ["case", "name", "prefix_path", "script_file", "upload_file", "desc"
        , "user", "add_time", "update_time"]
    list_filter = ["case", "name", "prefix_path", "user"]
    search_fields = ['name', ]


class TestTaskAdmin(object):
    list_display = ["name", "user", "task_state", "desc", "total_case_num", "success_case_num", "fail_case_num",
                    "block_case_num",
                    "execut_start_time", "execut_end_time", "execut_user"]
    list_filter = ["name", "user", "task_state", "desc", "total_case_num", "success_case_num", "fail_case_num",
                   "block_case_num",
                   "execut_start_time", "execut_end_time", "execut_user"]
    search_fields = ['name', ]

    class CaseReleteTestTaskInline(object):
        model = CaseReleteTestTask
        exclude = ['add_time', ]
        extra = 1
        style = 'tab'

    inlines = [CaseReleteTestTaskInline, ]


xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(ModuleCategory, ModuleCategoryAdmin)
xadmin.site.register(Case, CaseAdmin)
xadmin.site.register(CaseSet, CaseSetAdmin)
xadmin.site.register(CaseScript, CaseScriptAdmin)
xadmin.site.register(TestTask, TestTaskAdmin)
