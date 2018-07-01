from __future__ import absolute_import
from TestingPlatform.celery import app
from utils import adb
from .models import Device

import logging


@app.task
def device_check():
    logging.info("device_check")
    adbTools = adb.AdbTools()
    devices_que = adbTools.get_devices();
    source = devices_que['host']['ip']
    device_list = Device.objects.filter(source=source)
    device_list_online = devices_que['list']
    # devices_online_code = [device['code'] for device in devices_online['list']]
    new_devices = [device for device in device_list_online if device['code'] not in [d.code for d in device_list]]
    online_device = [device for device in device_list_online if device['code'] in [d.code for d in device_list]]
    offline_device = [device for device in device_list if device.code not in [d['code'] for d in device_list_online]]
    # 添加新设备
    for new in new_devices:
        name = new['name']
        code = new['code']
        source = source
        state = 'online'
        device_type = 'android'
        Device.objects.create(name=name, code=code, source=source, state=state, device_type=device_type)
    # 修改上线设备状态
    for online in online_device:
        code = online['code']
        Device.objects.filter(code=code, source=source).update(state='online')
    # 修改离线设备状态
    for offline in offline_device:
        code = offline.code
        Device.objects.filter(code=code, source=source).update(state='offline')
