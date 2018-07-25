import xadmin
from .models import DataBaseConfig, UrlDataConfig, TestDataConfig


class TestDataConfigAdmin(object):
    list_display = ["name", "type", "add_time"]
    search_fields = ['name', ]
    list_filter = ["name", "type", "add_time"]


class UrlDataConfigAdmin(object):
    list_display = ["test_data_config", "name", "keyword", "url", "add_time"]
    search_fields = ['name', ]
    list_filter = ["test_data_config", "name", "keyword", "url", "add_time"]


class DataBaseConfigAdmin(object):
    list_display = ["test_data_config", "name", "keyword", "database_host", "database_port", "database_user",
                    "database_password",
                    "add_time"]
    search_fields = ['name', ]
    list_filter = ["test_data_config", "name", "keyword", "database_host", "database_port", "database_user",
                   "database_password",
                   "add_time"]


xadmin.site.register(TestDataConfig, TestDataConfigAdmin)
xadmin.site.register(UrlDataConfig, UrlDataConfigAdmin)
xadmin.site.register(DataBaseConfig, DataBaseConfigAdmin)
