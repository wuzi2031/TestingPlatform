from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'apps.users'
    verbose_name = '用户管理'

    # def ready(self):
    #     # signals are imported, so that they are defined and can be used
    #     import apps.users.signals