from __future__ import absolute_import
from TestingPlatform.celery import app
import pika
from TestingPlatform import settings


class Connection:
    """
    connection
    """

    def __init__(self):
        credentials = pika.PlainCredentials(settings.BROKER_USER, settings.BROKER_PASS)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.BROKER_ADDR, port=settings.BROKER_PORT, credentials=credentials))

    def __enter__(self):
        return self.connection

    def getConnection(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


"""
topic模式
"""


def send(exchange, routing_key, body):
    with Connection() as connection:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='topic')
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)


@app.task
def receive(exchange, routing_keys, callback):
    """
    接收消息
    :param exchange:
    :param routing_keys: 路由列表
    :param callback: 结果回调
    :return:
    """
    connection = Connection().getConnection()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    for routing_key in routing_keys:
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
    print(' [*] Waiting for logs. To exit press CTRL+C')
    # no_ack=Fales:表示消费完以后不自动把状态通知rabbitmq
    channel.basic_consume(callback, queue=queue_name, no_ack=False)
    channel.start_consuming()
