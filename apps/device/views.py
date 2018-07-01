from .models import Device
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from .tasks import device_check
from .serializers import DeviceSerializer
# Create your views here.
class DeviceViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    # device_check.delay()
    print("dd")