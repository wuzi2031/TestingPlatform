from __future__ import absolute_import

import json
import logging

from cmq.tlib.run import run_case

from TestingPlatform.celery import app
from case.models import TestTask, CaseReleteTestTask
from dataconfig.models import DataBaseConfig, UrlDataConfig
from message import mq
from report.models import TaskExecuteInfo
from uitest.models import EnvConfig, RemoteService, ApKConfig, WebConfig, DeviceRelateApK
from .mqsetting import EXCHANGE, ROUTER_PER
from cmq.util import importlib

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
        for caseRelateTestTask in caseRelateTestTasks:
            # 中途手动停止
            task = TestTask.objects.filter(id=task_id).first()
            if task.task_state == 'stop':
                run_data['env_config'] = env.id
                run_data['script_type'] = 'python'
                run_data['option'] = 'stop'
                router = ROUTER_PER
                mq.send(exchange=EXCHANGE, routing_key=router + '.stop', body=json.dumps(run_data))
                stop = True
                break
            case = caseRelateTestTask.case
            script_path = case.case_script
            # 执行脚本
            print(script_path)
            # if os.getcwd() not in sys.path:
            #     sys.path.append(os.getcwd())
            logging.info("case_execute " + json.dumps(run_data))
            re = run_case(case_dir='cmq.demo', module_name='apiTest', param=json.dumps(run_data))
            logging.info(re)
            logging.info(re.failures)
            logging.info(re.errors)
            # 记录日志
            taskExecuteInfo = TaskExecuteInfo()
        if not stop:
            run_data['env_config'] = env.id
            run_data['script_type'] = 'python'
            run_data['option'] = 'finish'
            router = ROUTER_PER
            mq.send(exchange=EXCHANGE, routing_key=router + '.finish', body=json.dumps(run_data))
            task.task_state = 'finish'
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
