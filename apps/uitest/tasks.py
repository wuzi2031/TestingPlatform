from __future__ import absolute_import

import json
import logging
import time
from datetime import datetime

from cmq.tlib.run import run_case

from TestingPlatform import settings
from TestingPlatform.celery import app
from case.models import TestTask, CaseReleteTestTask, CaseScript
from dataconfig.models import DataBaseConfig, UrlDataConfig
from message import mq
from report.models import TaskExecuteInfo
from uitest.models import EnvConfig, RemoteService, ApKConfig, WebConfig, DeviceRelateApK
from .mqsetting import EXCHANGE, ROUTER_PER


# 工程目录执行celery -A TestingPlatform worker -l info
@app.task
def case_execute(*args, **kwargs):
    logging.info("case_execute " + str(kwargs['task_id']))
    task_id = kwargs['task_id']
    tasks = TestTask.objects.filter(id=task_id)

    if tasks:
        task = tasks.first()
        env = EnvConfig.objects.filter(task=task).first()
        run_data = gen_run_data(env)
        caseRelateTestTasks = CaseReleteTestTask.objects.filter(test_task=task).order_by('sort')
        stop = False
        task_start_time = datetime.now()
        re_execut_num = task.re_execut_num
        for caseRelateTestTask in caseRelateTestTasks:
            # 中途手动停止
            task = TestTask.objects.filter(id=task_id).first()
            if task.task_state == 'stop':
                stop = True
                break
            case = caseRelateTestTask.case
            case_scripts = CaseScript.objects.filter(case=case)
            if case_scripts:
                script_path = case_scripts.first().script_file.path
                # 执行脚本
                mc = gen_script_path(script_path)
                logging.info("case_execute " + json.dumps(run_data))
                # 记录日志
                taskExecuteInfo = TaskExecuteInfo()
                taskExecuteInfo.task = task
                taskExecuteInfo.case = case
                taskExecuteInfo.state = 'executing'
                taskExecuteInfo.save()
                start_time = time.time()
                if re_execut_num == None or re_execut_num == 0:
                    re_execut_num = 1
                while (re_execut_num > 0):
                    re = run_case(case_dir=mc[0], module_name=mc[1], param=json.dumps(run_data))
                    failures = re.failures
                    errors = re.errors
                    logging.info(re)
                    logging.info(failures)
                    logging.info(errors)
                    re_execut_num = re_execut_num - 1
                    if len(failures) == 0 and len(errors) == 0:
                        break
                    else:
                        if re_execut_num > 0:
                            print('失败重试: ' + case.title)

                if len(failures) > 0:
                    result = 'fail'
                    taskExecuteInfo.failure = failures[0]
                    fail_case_num = task.fail_case_num
                    if fail_case_num == None:
                        fail_case_num = 0
                    task.fail_case_num = fail_case_num + 1
                elif len(errors) > 0:
                    result = 'error'
                    taskExecuteInfo.error = errors[0]
                    fail_case_num = task.fail_case_num
                    if fail_case_num == None:
                        fail_case_num = 0
                    task.fail_case_num = fail_case_num + 1
                else:
                    result = 'success'
                    success_case_num = task.success_case_num
                    if success_case_num == None:
                        success_case_num = 0
                    task.success_case_num = success_case_num + 1
                end_time = time.time()
                taskExecuteInfo.result = result
                taskExecuteInfo.exec_time = int((end_time - start_time) * 1000)
                taskExecuteInfo.state = 'finish'
                taskExecuteInfo.save()
                task.save()

        run_data['env_config'] = env.id
        run_data['script_type'] = 'python'
        router = ROUTER_PER
        if not stop:
            run_data['option'] = 'finish'
            task.task_state = 'finish'
        else:
            run_data['option'] = 'stop'
        selenium_drivers = run_data['selenium_drivers']
        appium_drivers = run_data['appium_drivers']
        # 通知执行机清理环境
        if len(selenium_drivers) > 0 or len(appium_drivers) > 0:
            mq.send(exchange=EXCHANGE, routing_key=router + ".result", body=json.dumps(run_data))
        task.execut_start_time = task_start_time
        task.execut_end_time = datetime.now()
        success_case_num = task.success_case_num
        if not success_case_num:
            success_case_num = 0
        fail_case_num = task.fail_case_num
        if not fail_case_num:
            fail_case_num = 0
        bock_nums = task.total_case_num - success_case_num - fail_case_num
        task.block_case_num = bock_nums
        task.save()


def gen_run_data(env):
    run_date = {}
    # 数据配置
    testDataConfig = env.data_config
    # 数据库
    data_bases = DataBaseConfig.objects.filter(test_data_config=testDataConfig)
    # 遍历数据库
    if data_bases:
        dbs = {}
        for data_base in data_bases:
            key = data_base.keyword
            db = {}
            db['ENGINE'] = 'django.db.backends.mysql'
            db['NAME'] = data_base.name
            db['USER'] = data_base.database_user
            db['PASSWORD'] = data_base.database_password
            db['HOST'] = data_base.database_host
            dbs[key] = db
        run_date['data_bases'] = dbs
    # url
    urls = UrlDataConfig.objects.filter(test_data_config=testDataConfig)
    # 遍历url
    if urls:
        uri = {}
        for url in urls:
            key = url.keyword
            uri[key] = url.url
        run_date['urls'] = uri

    web_confgs = WebConfig.objects.filter(env=env)
    if web_confgs:
        # selenium_drivers
        sds = []
        for web_confg in web_confgs:
            sd = {}
            device = web_confg.device
            sd['host'] = device.source
            remote_device = RemoteService.objects.filter(env_config=env, host=device.source,
                                                         type='selenium').first()
            sd['port'] = remote_device.port
            sds.append(sd)
        run_date['selenium_drivers'] = sds
    apk_confs = ApKConfig.objects.filter(env=env)
    if apk_confs:
        # appium_drivers
        ads = []
        for apk_conf in apk_confs:
            app_package = apk_conf.package_name
            app_activity = apk_conf.package_start_activity
            device_re_apks = DeviceRelateApK.objects.filter(apKConfig=apk_conf)
            for device_re_apk in device_re_apks:
                device = device_re_apk.device
                ad = {}
                ad['device_name'] = device.code
                ad['app_package'] = app_package
                ad['app_activity'] = app_activity
                ad['host'] = device.source
                remote_device = RemoteService.objects.filter(env_config=env, host=device.source,
                                                             type='appium', device_code=device.code).first()
                ad['port'] = remote_device.port
                ad['platform_version'] = device.version
                adk = {}
                adk[device.name] = ad
                ads.append(adk)
        run_date['appium_drivers'] = ads
    return run_date


def gen_script_path(path):
    path = path.replace(settings.BASE_DIR + '/', '')
    path_arr = path.split('/')
    class_name = path_arr[-1].replace('.py', '')
    module_name = path.replace('/' + path_arr[-1], '').replace('/', '.')
    return module_name, class_name
