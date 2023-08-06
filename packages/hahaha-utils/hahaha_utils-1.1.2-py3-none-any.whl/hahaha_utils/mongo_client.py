# -*- coding: utf-8 -*-
'''
-------------------------------------------------
   File:           mongo_client.py
   Description:
   Author:        
   Create Date:    2020/07/21
-------------------------------------------------
   Modify:
                   2020/07/21:
-------------------------------------------------
'''
import pymongo
from log_handler import LogHandler


class MongodbClient:

    def __init__(self, database, datatable):
        self.logging = LogHandler('mongo_db')
        self.db_client = pymongo.MongoClient('mongodb://localhost:27017/')
        # 有密码验证时self.db_client = pymongo.MongoClient('mongodb://用户名:密码@ip:端口/'+database)#
        self.database = database
        self.db_name = self.db_client[database]
        self.collection_name = self.db_name[datatable]

    def check_database(self):
        db_list = self.db_client.list_database_names()
        if self.database in db_list:
            self.logging.info('数据库：%s 存在' % self.database)
            self.is_check_ok = 1
        else:
            self.logging.info('数据库：%s 不存在' % self.database)
            self.is_check_ok = 0

    def insert_one(self, tupstr):
        try:
            self.collection_name.insert_one(tupstr)
        except Exception as e:
            self.logging.info('执行函数：insert_one失败，错误信息%s' % e)

    def insert_many(self, listStr):
        try:
            self.collection_name.insert_many(listStr)
        except Exception as e:
            self.logging.info('执行函数：insert_many失败，错误信息：%s' % e)

    def find_one(self):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dit = self.collection_name.find_one()
            return dit
        except Exception as e:
            self.logging.info('执行函数：find_one失败，错误信息：%s' % e)

    def find_all(self):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dits = self.collection_name.find()
            return dits
        except Exception as e:
            self.logging.info('执行函数：find_all失败，错误信息%s' % e)

    def find_partShow(self, rules):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dits = self.collection_name.find({}, rules)
            return dits
        except Exception as e:
            self.logging.info('执行函数：find_partShow失败，错误信息%s' % e)

    def find_rules(self, rules):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dits = self.collection_name.find(rules)
            return dits
        except Exception as e:
            self.logging.info('执行函数：find_rules失败，错误信息%s' % e)

    def find_limit(self, num):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dits = self.collection_name.find().limit(num)
            return dits
        except Exception as e:
            self.logging.info('执行函数：find_limit失败，错误信息%s' % e)

    def update_one(self, rules, newValue):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            self.collection_name.update_one(rules, newValue)
        except Exception as e:
            self.logging.info('执行函数：updata_one失败，错误信息%s' % e)

    def update_many(self, rules, newValue):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return
            dits = self.collection_name.update_one(rules, newValue)
            return dits
        except Exception as e:
            self.logging.info('')

    def sort(self, key, order=1):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return

            data = self.collection_name.find().sort(key, order)
            return data
        except Exception as e:
            self.logging.info('执行函数：sort 失败:错误信息%s' % e)

    def delete_one(self, rule):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return

            self.collection_name.delete_one(rule)
        except Exception as e:
            self.logging.info('执行函数delete_one失败，错误信息%s' % e)

    def delete_many(self, rules):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return

            self.collection_name.delete_many(rules)
        except Exception as e:
            self.logging.info('执行函数delete_many失败，错误信息%s' % e)

    def delete_all(self):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return

            self.collection_name.delete_many({})
        except Exception as e:
            self.logging.info('执行函数delete_all失败，错误信息%s' % e)

    def drop(self):
        try:
            self.check_database()
            if self.is_check_ok == 0:
                return

            self.collection_name.drop()
        except Exception as e:
            self.logging.info('执行函数drop失败，错误信息%s' % e)


if __name__ == '__main__':
    pass