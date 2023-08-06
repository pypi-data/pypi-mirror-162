# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           kafka_producter.py
   Description:    kafka 生产者
   Author:        
   Create Date:    2020/08/04
-------------------------------------------------
   Modify:
                   2020/08/04:
-------------------------------------------------
"""
from __future__ import division
import json
import base64
import datetime
from kafka import KafkaProducer

TS = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
files = {
    "name": 'test_content',
    "data": 'Data'
}
producer = KafkaProducer(
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    bootstrap_servers='127.0.0.1:9092'
)
for i in range(3):
    print('i: ', files)
    producer.send('test', files)

producer.close()