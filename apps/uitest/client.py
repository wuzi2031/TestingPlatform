import requests, pika

# mq地址
BROKER_ADDR = "120.79.16.35"
# mq端口号
BROKER_PORT = 5672
# mq用户
BROKER_USER = "admin"
# mq密码
BROKER_PASS = "admin"


def receive(exchange, routing_keys, callback):
    """
    接收消息
    :param exchange:
    :param routing_keys: 路由列表
    :param callback: 结果回调
    :return:
    """
    credentials = pika.PlainCredentials(BROKER_USER, BROKER_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=BROKER_ADDR, port=BROKER_PORT, credentials=credentials))
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


def callback(self, ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    receive("test_plat_topic", ["task.#"], callback)
