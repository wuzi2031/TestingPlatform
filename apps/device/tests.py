from django.test import TestCase
from device.views import device_check
# Create your tests here.
class DeviceTest(TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_device_check(self):
        device_check()