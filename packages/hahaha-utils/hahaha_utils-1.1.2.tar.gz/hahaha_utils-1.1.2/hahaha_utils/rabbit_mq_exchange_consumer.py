# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           rabbit_mq_exchange_consumer.py
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
import sys
import json

hostname = '127.0.0.1'
port = 5672
username = 'guest'
password = 'root'
exchange = 'etl.topic'
queue = 'test'
queue1 = 'test1'

credentials = pika.PlainCredentials(username=username, password=password)
parameters = pika.ConnectionParameters(host=hostname,port=port,credentials=credentials)
connection = pika.BlockingConnection(parameters=parameters)#创建连接

channel = connection.channel()
channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

result = channel.queue_declare(exclusive=False, queue=queue, durable=True)
channel.queue_declare(exclusive=False, queue=queue1, durable=True)

#绑定键。‘#’匹配所有字符，‘*’匹配一个单词
binding_key = queue

# if not binding_keys:
#     sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
#     sys.exit(1)

# for binding_key in binding_keys:
#     print(binding_key)

channel.queue_bind(exchange=exchange, queue=queue, routing_key=binding_key)

print('[*] Writing for logs. To exit press CTRL+C.')


def parse(data):
    json_data = json.loads(data)
    json_data['fcreate_time'] = json_data['fcreate_time'].replace('T', ' ').replace('.000Z', '')
    json_data['fapproval_suc_time'] = json_data['fapproval_suc_time'].replace('T', ' ').replace('.000Z', '')
    json_data['fmodify_time'] = json_data['fmodify_time'].replace('T', ' ').replace('.000Z', '')
    try:
        json_data['fnext_follow_time'] = json_data['fnext_follow_time'].replace('T', ' ').replace('.000Z', '')
    except Exception as e:
        print(e)

    try:
        json_data['flast_modify_time'] = json_data['flast_modify_time'].replace('T', ' ').replace('.000Z', '')
    except Exception as e:
        print(e)
    print(json_data)

def callback(ch, method, properties, body):
    # print(ch)
    # print(method)
    # print(properties)
    # print(method.routing_key, body.decode())
    data = body.decode()
    parse(data)



channel.basic_consume(on_message_callback=callback, queue=queue, auto_ack=True)
channel.basic_consume(on_message_callback=callback, queue=queue1, auto_ack=True)
channel.start_consuming()
