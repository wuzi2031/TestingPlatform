from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import TestDataConfig, DeviceRelateEnv, EnvConfig, DataBaseConfig
from .serializers import TestDataConfigSerializer, DeviceRelateEnvSerializer, EnvConfigSerializer, \
    DataBaseConfigSerializer
from case.models import TestTask
from datetime import datetime
from message import mq
from .mqsetting import EXCHANGE, ROUTER_PER
from device.models import Device
import json
from utils.mode import modelToJson
from django.contrib.auth import get_user_model

User = get_user_model()


class TestDataConfigViewSet(viewsets.ModelViewSet):
    """
    测试数据配置
    """
    queryset = TestDataConfig.objects.all()
    serializer_class = TestDataConfigSerializer


class DataBaseConfigViewSet(viewsets.ModelViewSet):
    """
    测试数据配置
    """
    queryset = DataBaseConfig.objects.all()
    serializer_class = DataBaseConfigSerializer


class DeviceRelateEnvViewSet(viewsets.ModelViewSet):
    """
    设备选择
    """
    queryset = DeviceRelateEnv.objects.all()
    serializer_class = DeviceRelateEnvSerializer

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
                devices = DeviceRelateEnv.objects.filter(env=env_config)
                if (not devices):
                    Response("请选择设备")
                mq_dict = {}
                app_path = ""
                if env_config.app:
                    app_path = env_config.app.url
                test_app_path = ""
                if env_config.test_app:
                    test_app_path = env_config.test_app.url
                script_type = env_config.app_script_type
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
