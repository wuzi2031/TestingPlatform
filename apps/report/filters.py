import django_filters

from case.models import TestTask


# 自定义的过滤类，需要继承django_filter.rest_framework中的FilterSet类
class TaskFilter(django_filters.rest_framework.FilterSet):
    execut_start_time = django_filters.DateRangeFilter(field_name="execut_start_time", label='执行开始时间')
    task_state = django_filters.MultipleChoiceFilter(choices=TestTask.TASK_STATE, label='任务状态')

    class Meta:
        model = TestTask
        fields = ['task_state', 'execut_start_time']
