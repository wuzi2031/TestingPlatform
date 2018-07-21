import json
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from case.models import TestTask
from message import mq
from utils.mode import modelToJson
from .models import EnvConfig, ApKConfig, DeviceRelateApK
from .mqsetting import EXCHANGE, ROUTER_PER
from .serializers import DeviceRelateApKSerializer, EnvConfigSerializer

User = get_user_model()


class DeviceRelateApKViewSet(viewsets.ModelViewSet):
    """
    设备选择
    """
    queryset = DeviceRelateApK.objects.all()
    serializer_class = DeviceRelateApKSerializer

    def perform_destroy(self, instance):
        device = instance.device
        device.is_used = False
        device.save()
        instance.delete()


class EnvConfigViewSet(viewsets.ModelViewSet):
    """
    任务环境配置
    """
    queryset = EnvConfig.objects.all()
    serializer_class = EnvConfigSerializer
    lookup_field = "task"


class TaskStartView(APIView):
    def post(self, request):
        """
        开始执行任务
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.data.items():
            processed_dict[key] = value
        task_id = processed_dict.pop('task_id', None)
        execut_user = request.user
        if (task_id):
            test_task = TestTask.objects.filter(id=task_id)[0]
            task_state = test_task.task_state
            if (task_state == 'executing'):
                return Response("任务正在执行")
            else:
                env_configs = EnvConfig.objects.filter(task=test_task)
                if (not env_configs):
                    Response("请配置环境数据")
                env_config = env_configs[0]
                apkConfigs = ApKConfig.objects.filter(env=env_config)

                for apkConfig in apkConfigs:
                    app_path = ""
                    if apkConfig.app:
                        app_path = apkConfig.app.url
                    test_app_path = ""
                    if apkConfig.test_app:
                        test_app_path = apkConfig.test_app.url
                    re_devices = DeviceRelateApK.objects.filter(apKConfig=apkConfig)
                    if (not re_devices):
                        Response("请选择设备")
                    for re_device in re_devices:
                        mq_dict = {}
                        script_type = env_config.app_script_type
                        mq_dict['env_config'] = env_config.id
                        mq_dict['script_type'] = script_type
                        mq_dict['app'] = app_path
                        mq_dict['test_app'] = test_app_path
                        mq_dict['devices'] = [modelToJson(device) for device in devices]
                        test_task.task_state = "executing"
                        test_task.execut_start_time = datetime.now()
                        test_task.execut_user = execut_user
                        test_task.save()
                        router = ROUTER_PER
                        mq.send(exchange=EXCHANGE, routing_key=router, body=json.dumps(mq_dict))
                return Response("success")
        return Response("fail")


class ClientReadyView(APIView):
    """
    执行机准备情况通知
    """

    def post(self, request):
        return Response("success")
