# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           rabbit_mq_producer.py
   Description:    RabbitMQ 生产者
   Author:        
   Create Date:    2020/08/04
-------------------------------------------------
   Modify:
                   2020/08/04:
-------------------------------------------------
"""
import pika
import json

credentials = pika.PlainCredentials('guest', 'root')  # mq用户名和密码
# 虚拟队列需要指定参数 virtual_host，如果是默认的可以不填。
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()
# 声明消息队列，消息将在这个队列传递，如不存在，则创建
result = channel.queue_declare(queue='hello', durable = True)

for i in range(10):
    message = json.dumps({'OrderId': "1000%s" % i})
    # 向队列插入数值 routing_key是队列名
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    print(message)
connection.close()
