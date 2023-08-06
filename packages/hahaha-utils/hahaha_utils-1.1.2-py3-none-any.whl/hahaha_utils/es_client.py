# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           es_client.py
   Description:
   Author:        
   Create Date:    2021/04/25
-------------------------------------------------
   Modify:
                   2021/04/25:
-------------------------------------------------
"""
from elasticsearch import Elasticsearch
from hahaha_utils.log_handler import LogHandler

class ES_Client(object):
    def __init__(self,es_host, http_auth=None):
        self.log = LogHandler('es')
        self.es = Elasticsearch(es_host, http_auth=http_auth)

    def fetch_data(self, index, size, body):
        data_list = []

        try:
            results = self.es.search(index=index, size=size, body=body)['hits']['hits']
            for data in results:
                data_list.append(data)
        except Exception as e:
            self.log.info('数据查询失败: ' + str(e))
        
        return data_list