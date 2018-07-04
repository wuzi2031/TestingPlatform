from django.test import TestCase
from .mq import send, receive


# Create your tests here.
class Mqtest(TestCase):
    def test_mq_send(self):
        send("test_plat_topic", "task1.android.equpment1", "{name:hi,pass:heihei}")

    def callback(self, ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def test_yesmq_receive(self):
        receive("test_plat_topic", ["task1.#"], self.callback)
