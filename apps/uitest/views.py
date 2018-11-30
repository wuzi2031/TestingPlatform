import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from case.models import TestTask
from device.models import Device
from message import mq
from utils.mode import modelToJson
from .models import EnvConfig, ApKConfig, DeviceRelateApK, RemoteService, WebConfig
from .mqsetting import EXCHANGE, ROUTER_PER
from .serializers import DeviceRelateApKSerializer, EnvConfigSerializer, ApKConfigSerializer, WebConfigSerializer
from .tasks import case_execute

User = get_user_model()


class ApKConfigViewSet(viewsets.ModelViewSet):
    """
    apk配置
    """
    queryset = ApKConfig.objects.all()
    serializer_class = ApKConfigSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('env',)
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


class WebConfigViewSet(viewsets.ModelViewSet):
    """
    web设备配置
    """
    queryset = WebConfig.objects.all()
    serializer_class = WebConfigSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('env',)
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def perform_destroy(self, instance):
        device = instance.device
        device.is_used = False
        device.save()
        instance.delete()


class DeviceRelateApKViewSet(viewsets.ModelViewSet):
    """
    apk设备选择
    """
    queryset = DeviceRelateApK.objects.all()
    serializer_class = DeviceRelateApKSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('apKConfig',)
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

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
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('task',)
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证


class TaskStartView(APIView):
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

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
                return Response(status=status.HTTP_201_CREATED, data={"任务正在执行"})
            else:
                env_configs = EnvConfig.objects.filter(task=test_task)
                if (not env_configs):
                    Response(status=status.HTTP_201_CREATED, data={"请配置环境数据"})
                env_config = env_configs[0]
                apkConfigs = ApKConfig.objects.filter(env=env_config)
                mq_dict = {}
                script_type = env_config.app_script_type
                mq_dict['env_config'] = env_config.id
                mq_dict['script_type'] = script_type
                mq_dict['option'] = mq.Option.START.value
                web_configs = WebConfig.objects.filter(env=env_config)
                # web自动化设备
                webs = []
                if web_configs:
                    for web_config in web_configs:
                        wb = {}
                        pc = web_config.device
                        wb['host'] = pc.source
                        wb['name'] = pc.name
                        webs.append(wb)
                mq_dict['webs'] = webs
                # app自动化设备
                apps = []
                if apkConfigs:
                    for apkConfig in apkConfigs:
                        ac = {}
                        app_path = ""
                        if apkConfig.app:
                            app_path = apkConfig.app.url
                        test_app_path = ""
                        if apkConfig.test_app:
                            test_app_path = apkConfig.test_app.url
                        re_devices = DeviceRelateApK.objects.filter(apKConfig=apkConfig)
                        if (not re_devices):
                            Response(status=status.HTTP_201_CREATED, data={"请选择设备"})
                        ac['app'] = app_path
                        ac['package_name'] = apkConfig.package_name
                        ac['test_app'] = test_app_path
                        ac['devices'] = [modelToJson(re_device.device) for re_device in re_devices]
                        apps.append(ac)
                mq_dict['apps'] = apps
                test_task.task_state = "executing"
                test_task.execut_start_time = datetime.now()
                # test_task.execut_user = execut_user
                test_task.save()
                router = ROUTER_PER
                mq.send(exchange=EXCHANGE, routing_key=router + '.start', body=json.dumps(mq_dict))
                return Response(status=status.HTTP_201_CREATED, data=mq_dict)
        return Response(status=status.HTTP_201_CREATED, data={'fail'})


class TaskStopView(APIView):
    permission_classes = (IsAuthenticated,)  # 登录验证
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)  # jwt验证

    def post(self, request):
        """
        停止执行任务
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
            if (not task_state == 'executing'):
                test_task.task_state = 'stop'
                test_task.save()
                Response(status=status.HTTP_201_CREATED, data={"success"})
            else:
                Response(status=status.HTTP_201_CREATED, data={"不能进行该操作"})


class ClientReadyView(APIView):
    """
    执行机准备情况通知
    """

    def post(self, request):
        processed_dict = request.data
        env_config_id = processed_dict['env_config']
        servivce_list = processed_dict['servivce_list']
        env_configs = EnvConfig.objects.filter(id=env_config_id)
        if (not env_configs):
            Response(status=status.HTTP_201_CREATED, data={"环境数据不存在"})
        env_config = env_configs[0]

        device_codes = list()
        hosts = list()

        if servivce_list:
            for service in servivce_list:
                remoteService = RemoteService.objects.filter(env_config=env_config, host=service['host'],
                                                             port=service['port']).first()
                if not remoteService:
                    remoteService = RemoteService()
                type = service['type']
                remoteService.type = type
                remoteService.host = service['host']
                remoteService.port = str(service['port'])
                if type == 'appium':
                    remoteService.keyword = service['device_name']
                    remoteService.device_name = service['device_name']
                    remoteService.device_code = service['device_code']
                remoteService.env_config = env_config
                remoteService.save()
                if type == 'appium':
                    device_codes.append(service['device_code'])
                elif type == 'sele':
                    hosts.append(service['host'])
            all_ready = True
            apkConfigs = ApKConfig.objects.filter(env=env_config)
            if apkConfigs:
                ders = DeviceRelateApK.objects.filter(apKConfig__in=apkConfigs)
                for der in ders:
                    if der.device.code in device_codes:
                        der.ready = True
                        der.save()
                    if not der.ready:
                        all_ready = der.ready
            webConfigs = WebConfig.objects.filter(env=env_config)
            if webConfigs:
                for webConfig in webConfigs:
                    if webConfig.device.source in hosts:
                        webConfig.ready = True
                        webConfig.save()
                    if not webConfig.ready:
                        all_ready = der.ready
            if all_ready:
                # 开始执行
                task = env_config.task
                case_execute.delay(task_id=task.id)
            else:
                return Response(status=status.HTTP_201_CREATED, data={'fail'})
        return Response(status=status.HTTP_201_CREATED, data={'success'})


class ClientEnvCleaerView(APIView):
    """
    执行机环境清理情况通知
    """

    def post(self, request):
        processed_dict = request.data
        env_config_id = processed_dict['env_config']
        host = processed_dict['host']
        env_configs = EnvConfig.objects.filter(id=env_config_id)
        if (not env_configs):
            Response(status=status.HTTP_201_CREATED, data={"环境数据不存在"})
        env_config = env_configs[0]
        remote_services = RemoteService.objects.filter(env_config=env_config, host=host)
        for remote_service in remote_services:
            type = remote_service.type
            if type == 'selenium':
                pc = Device.objects.filter(source=host, device_type='pc').first()
                pc.is_used = False
                pc.save()
            elif type == 'appium':
                code = remote_service.device_code
                device = Device.objects.filter(source=host, code=code).first()
                device.is_used = False
                device.save()
        return Response(status=status.HTTP_201_CREATED, data={'success'})
