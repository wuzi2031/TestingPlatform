import xadmin
from .models import Device


class DeviceAdmin(object):
    list_display = ["name", "code", "env_type", "device_type", "state", "source", "is_used", "add_time"]
    search_fields = ['name', ]
    list_filter = ["name", "code", "env_type", "device_type", "state", "source", "is_used", "add_time"]


xadmin.site.register(Device, DeviceAdmin)
