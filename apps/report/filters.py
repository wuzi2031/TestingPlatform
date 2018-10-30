import django_filters

from case.models import TestTask
from .models import TaskExecuteInfo


# 自定义的过滤类，需要继承django_filter.rest_framework中的FilterSet类
class TaskFilter(django_filters.rest_framework.FilterSet):
    execut_start_time = django_filters.DateRangeFilter(field_name="execut_start_time", label='执行开始时间')
    task_state = django_filters.MultipleChoiceFilter(choices=TestTask.TASK_STATE, label='任务状态')

    class Meta:
        model = TestTask
        fields = ['task_state', 'execut_start_time']


class ReportCaseListFilter(django_filters.rest_framework.FilterSet):
    task = django_filters.NumberFilter(field_name="task", label='任务')
    case_title = django_filters.CharFilter(method='case_title_filter', label='用例标题')

    def case_title_filter(self, queryset, name, value):
        return queryset.filter(case__title__contains=value)

    class Meta:
        model = TaskExecuteInfo
        fields = ['task', 'case_title']
