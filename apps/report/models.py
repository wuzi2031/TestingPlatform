from datetime import datetime

from django.db import models

from case.models import TestTask, Case


# Create your models here.
class TaskExecuteInfo(models.Model):
    STATE = (
        ("executing", "执行中"),
        ("block", "执行中断"),
        ("finish", "执行完成")
    )
    RESULT = (
        ("success", "成功"),
        ("fail", "失败"),
        ("error", "错误")
    )
    ANALYSE = (
        ("non_analyse", "未分析"),
        ("bug", "产品BUG"),
        ("script_error", "脚本错误")
    )
    task = models.ForeignKey(TestTask, related_name='task_execute_info', verbose_name='测试任务')
    case = models.ForeignKey(Case, verbose_name='测试用例')
    state = models.CharField(max_length=30, default='executing', choices=STATE, verbose_name="状态")
    result = models.CharField(max_length=30, null=True, blank=True, choices=RESULT, verbose_name="结果")
    failure = models.TextField(verbose_name="失败原因")
    error = models.TextField(verbose_name="错误原因")
    exec_time = models.IntegerField(verbose_name="执行时长")
    analyse_result = models.CharField(max_length=30, default='non_analyse', choices=ANALYSE, verbose_name="分析结果")
    analyse_comments = models.TextField(null=True, blank=True, verbose_name="分析说明")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "任务执行信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.case.title
