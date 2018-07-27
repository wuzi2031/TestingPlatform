from datetime import datetime

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Device
from .serializers import DeviceSerializer


# Create your views here.
class DeviceViewSet(viewsets.ModelViewSet):
    """
    设备管理
    list:
        设备列表
    update:
        修改设备
    destroy:
        删除设备
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    # device_check.delay()


class DeviceSyncView(APIView):
    def post(self, request):
        """
        安卓和pc数据同步
        :param request:
        :return:
        """
        processed_dict = request.data
        print(processed_dict)
        host = processed_dict['host']
        host_name = host['name']
        source = host['ip']
        pc_list = Device.objects.filter(source=source, device_type='pc')

        if pc_list:
            pc = pc_list[0]
            pc.state = 'online'
            pc.sync_time = datetime.now()
            pc.save()
        else:
            Device.objects.create(name=host_name, code="", source=source, state='online',
                                  device_type="pc")
        device_list = Device.objects.filter(source=source, device_type__contains='android')
        device_list_online = processed_dict['list']
        # devices_online_code = [device['code'] for device in devices_online['list']]
        new_devices = [device for device in device_list_online if device['code'] not in [d.code for d in device_list]]
        online_device = [device for device in device_list_online if device['code'] in [d.code for d in device_list]]
        offline_device = [device for device in device_list if
                          device.code not in [d['code'] for d in device_list_online]]
        # 添加新设备
        for new in new_devices:
            name = new['name']
            code = new['code']
            source = source
            state = 'online'
            Device.objects.create(name=name, code=code, source=source, state=state,
                                  device_type=self.getDeviceType(name))
        # 修改上线设备状态
        for online in online_device:
            code = online['code']
            Device.objects.filter(code=code, source=source).update(state='online', sync_time=datetime.now())
        # 修改离线设备状态
        now = datetime.now()
        for offline in offline_device:
            code = offline.code
            offd = Device.objects.filter(code=code, source=source)[0]
            sync_time = offd.sync_time
            if (now - sync_time).seconds > 60:
                offd.state = 'offline'
                offd.save()
        pcs = Device.objects.filter(device_type='pc')
        for pc in pcs:
            sync_time = pc.sync_time
            if (now - sync_time).seconds > 60:
                pc.state = 'offline'
                pc.save()
        return Response(status=status.HTTP_201_CREATED, data={'success'})

    def getDeviceType(self, name):
        pos_dict = {"DP900", "DP700", "DP760"}
        if name.upper() in pos_dict:
            return "android_pos"
        else:
            return "android_mobile"
