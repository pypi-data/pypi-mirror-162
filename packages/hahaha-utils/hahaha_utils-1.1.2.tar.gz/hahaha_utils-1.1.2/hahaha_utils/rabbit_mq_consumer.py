# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           rabbit_mq_consumer.py
   Description:    RabbitMQ 消费者
   Author:        
   Create Date:    2020/08/04
-------------------------------------------------
   Modify:
                   2020/08/04:
-------------------------------------------------
"""
import pika
queue = 'test'
credentials = pika.PlainCredentials('guest', 'root')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=queue, durable = True)


def callback(ch, method, properties, body):
    # print(method.delivery_tag)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    print(body.decode())
    # print(" [x] Received %r" % body)
    # print(properties)


channel.basic_consume(
    queue=queue, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()