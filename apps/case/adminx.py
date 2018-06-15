import xadmin
from .models import Product, ModuleCategory, Case, CaseScript, ScriptExcConfig


class ProductAdmin(object):
    list_display = ["name", "code", "desc", "product_type", "package_name", "add_time"]
    search_fields = ['name', ]
    list_filter = ["name", "code", "desc", "product_type", "package_name", "add_time"]


class ModuleCategoryAdmin(object):
    list_display = ["name", "product_category", "code", "desc", "parent_category", "add_time"]
    list_filter = ["product_category", "parent_category", "name"]
    search_fields = ['name', ]


class CaseAdmin(object):
    list_display = ["product_module", "title", "create_user", "case_type", "test_type", "test_precondition",
                    "test_step", "enclosure_title", "enclosure", "is_del", "add_time", "update_time"]
    list_filter = ["title", "product_module", "case_type", "test_type", "is_del"]
    search_fields = ['title', ]


class ScriptExcConfigAdmin(object):
    list_display = ["prefix_path", ]


class CaseScriptAdmin(object):
    list_display = ["case", "script_name", "script_exc_config", "script_file", "upload_file", "desc",
                    "is_del", "add_time", "update_time"]
    list_filter = ["case", "script_name", "script_exc_config", "is_del"]
    search_fields = ['script_name', ]


xadmin.site.register(Product, ProductAdmin)
xadmin.site.register(ModuleCategory, ModuleCategoryAdmin)
xadmin.site.register(Case, CaseAdmin)
xadmin.site.register(ScriptExcConfig, ScriptExcConfigAdmin)
xadmin.site.register(CaseScript, CaseScriptAdmin)
