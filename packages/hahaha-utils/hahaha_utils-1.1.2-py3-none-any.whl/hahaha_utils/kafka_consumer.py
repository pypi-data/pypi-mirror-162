# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           kafka_consumer.py
   Description:    kafka 消费者
   Author:        
   Create Date:    2020/08/04
-------------------------------------------------
   Modify:
                   2020/08/04:
-------------------------------------------------
"""
from __future__ import division
import sys
import json
from kafka import KafkaConsumer

KAFKA_TOPIC = 'Dhg'
KAFKA_BROKERS = '127.0.0.1:9092'
topic = 'test'
consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKERS, auto_offset_reset='earliest')
consumer.subscribe([KAFKA_TOPIC, topic])
try:
    for message in consumer:
        print(message)
        data = json.loads(message.value.decode())
        print(data)
        try:
            for i in json.loads(data['name']):
                print(i)
        except:
            pass
        try:
            for j in json.loads(data['data']):
                print(j)
        except:
            pass

except KeyboardInterrupt:
    sys.exit()