# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           rabbit_mq_exchange_producter.py
   Description:
   Author:        
   Create Date:    2020/08/04
-------------------------------------------------
   Modify:
                   2020/08/04:
-------------------------------------------------
"""
# -*- coding: utf-8 -*-

import pika

hostname = '127.0.0.1'
port = 5672
username = 'guest'
password = 'root'
routing_key = 'test_routing'
credentials = pika.PlainCredentials(username=username, password=password)
parameters = pika.ConnectionParameters(host=hostname, port=port, credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)  # 创建连接

channel = connection.channel()

# 创建模糊匹配的exchange
channel.exchange_declare(exchange='data_sync', exchange_type='topic', durable=True)

# 这里关键字必须为点号隔开的单词，以便于消费者进行匹配。
routing_key = routing_key
# routing_key = '[warn].kern'

message = 'Hello World!'
channel.basic_publish(exchange='data_sync', routing_key=routing_key, body=message)

print('[生产者] Send %r:%r' % (routing_key, message))
connection.close()
