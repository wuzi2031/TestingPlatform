from __future__ import absolute_import

import logging

from TestingPlatform.celery import app


@app.task
def case_execute(*args, **kwargs):
    logging.info("case_execute " + str(kwargs['task']))
    # caseReleteTestTask = CaseReleteTestTask.objects.filter(test_task=task).order_by('sort').first()
    # case = caseReleteTestTask.case
    # print(case.title)
    # # 记录日志
    # taskExecuteInfo = TaskExecuteInfo()
