from rest_framework import serializers
from .models import Device
from datetime import datetime
from django.db import transaction


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
