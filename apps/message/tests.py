from django.test import TestCase

from .mq import send, receive
import json

# Create your tests here.
class Mqtest(TestCase):
    def test_mq_send(self):
        date = {
            "data_bases": {
                "not_trade": {
                    "ENGINE": "django.db.backends.mysql",
                    "NAME": "ci非订单库",
                    "USER": "qgd_stf_wt_qa",
                    "PASSWORD": "PhEG6KP2nHsCnOz9jRfE",
                    "HOST": "ci.rdsmaster.cnhz.shishike.com"
                },
                "local": {
                    "ENGINE": "django.db.backends.mysql",
                    "NAME": "本地测试数据库",
                    "USER": "root",
                    "PASSWORD": "Wzm@123456",
                    "HOST": "127.0.0.1"
                }
            },
            "urls": {
                "mind": "http://citestcalm.shishike.com",
                "erp": "http://citesterp.shishike.com"
            },
            "selenium_drivers": [
                {
                    "host": "192.168.10.171",
                    "port": "4444"
                }
            ],
            "appium_drivers": [
                {
                    "DP760": {
                        "device_name": "P1QRMRZH04",
                        "app_package": "com.shishike.calm",
                        "app_activity": "com.shishike.calm.splash.KouBeiLogoAcitivty_",
                        "host": "192.168.10.171",
                        "port": "4723",
                        "platform_version": ""
                    }
                }
            ],
            "env_config": 2,
            "script_type": "python",
            "option": "finish"
        }

        send("test_plat_topic", "task.finish", json.dumps(date))

    def callback(self, ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def test_yesmq_receive(self):
        receive("test_plat_topic", ["task1.#"], self.callback)
