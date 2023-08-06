# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           canal_client.py
   Description:
   Author:        
   Create Date:    2022/04/26
-------------------------------------------------
   Modify:
                   2022/04/26:
-------------------------------------------------
"""
import time
from canal.client import Client
from canal.protocol import EntryProtocol_pb2


class CanalClient(object):
    """
    对canal进行封装
    """
    def __init__(self, canal_config=None):
        canal_host = canal_config['canal_host']
        canal_port = canal_config['canal_port']
        canal_user = canal_config['canal_user']
        canal_pass = canal_config['canal_pass']
        self.client = Client()
        self.client.connect(host=canal_host, port=canal_port)
        self.client.check_valid(username=canal_user, password=canal_pass)

    def parse_after_data(self, row_data, exclude_fields):
        """
        解析变更之前的数
        :param row_data:
        :return:
        """
        insert_data_list = []
        data_list = {}
        row_field_list = []
        row_data_list = []
        for column in row_data.afterColumns:
            if column.name not in exclude_fields:
                row_field_list.append(column.name)
                row_data_list.append(column.value)
        return row_field_list, row_data_list
        # print(row_field_list)
        # print(row_data_list)

    def parse_before_data(self, row_data, exclude_fields):
        """
        解析变更之后的数据
        :param row_data:
        :return:
        """
        data_list = {}
        row_field_list = []
        row_data_list = []
        for column in row_data.beforeColumns:
            if column.name not in exclude_fields:
                row_field_list.append(column.name)
                row_data_list.append(column.value)
            # print(row_field_list)
            # print(row_data_list)
        return list(set(row_field_list))[0], row_data_list

    def subscribe_message(self, client_id=b'1001', destination=b'collect_db', filter=b'collection_db.t_collection_case'):
        """
        订阅消息
        :param client_id:
        :param destination:
        :param filter:
        :return:
        """
        # 订阅消息
        self.client.subscribe(client_id=client_id, destination=destination, filter=filter)

    def parse_data(self, batch_size=100, exclude_fields=None):
        """
        解析数据
        :param batch_size:
        :return:
        """
        if exclude_fields is None:
            exclude_fields = []

        message = self.client.get(batch_size)
        entries = message['entries']

        # 声明变更前的数据列表，主要装delete的前数据
        before_data_list = []

        # 声明变更后的数据列表，主要装insert, update后的数据
        after_data_list = []

        # 声明字段列表
        field_list = []

        # 遍历entries
        for entry in entries:

            #　获取entry的类型
            entry_type = entry.entryType

            # 跳过事务
            if entry_type in [EntryProtocol_pb2.EntryType.TRANSACTIONBEGIN, EntryProtocol_pb2.EntryType.TRANSACTIONEND]:
                continue

            # 获取变更的数据行
            row_change = EntryProtocol_pb2.RowChange()
            row_change.MergeFromString(entry.storeValue)

            # event_type = row_change.eventType
            # print(event_type, '111111111111111111111111')

            # 获取消息头
            header = entry.header

            # 获取数据源的数据库名称
            database = header.schemaName

            # 获取数据源的表名称
            table = header.tableName

            # 事件类型
            event_type = header.eventType
            # print(event_type, '2222222222222222222222222')

            # 遍历更改的行字段
            for row in row_change.rowDatas:

                format_data = {}
                format_data['before'] = {}
                format_data['after'] = {}
                row_data = []
                # 根据事件类型来分别解析数据
                if event_type == EntryProtocol_pb2.EventType.DELETE:
                    # print('delete sql')
                    field_list, row_data = self.parse_before_data(row, exclude_fields)
                    before_data_list.append(tuple(row_data))
                elif event_type == EntryProtocol_pb2.EventType.INSERT:
                    # print('insert sql')
                    field_list, row_data = self.parse_after_data(row, exclude_fields)
                    after_data_list.append(tuple(row_data))
                elif event_type == EntryProtocol_pb2.EventType.UPDATE:
                    # print('update sql')
                    field_list, row_data = self.parse_after_data(row, exclude_fields)
                    after_data_list.append(tuple(row_data))
                # print(row_data)
                # data = dict(
                #     db=database,
                #     table=table,
                #     event_type=event_type,
                #     data=format_data,
                # )
                # print(data)
        # print('insert_data_list: ', len(insert_data_list))
        # print('delete_data_list: ', len(delete_data_list))
        # print('update_data_list: ', len(update_data_list))
        # print('####################################################################')
        # time.sleep(1)

        if len(field_list) == 0:
            return [], []
        else:
            return field_list, after_data_list

    def close_canal(self):
        try:
            self.client.disconnect()
        except Exception as e:
            pass


if __name__ == '__main__':

    canal_config = {
        'canal_host': '127.0.0.1',
        'canal_port': 11111,
        'canal_user': b'',
        'canal_pass': b''
    }

    client_id = b'1001'
    destination = b'instance_name'
    filter = b'db_name.*\\.table_name.*'
    batch_size = 10

    client = CanalClient(canal_config)
    client.subscribe_message(client_id, destination, filter)

    while True:
        field_list, data_list = client.parse_data(batch_size)
    client.close_canal()




