# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           parse_sql.py
   Description:
   Author:        
   Create Date:    2020/10/14
-------------------------------------------------
   Modify:
                   2020/10/14:
-------------------------------------------------
"""
sql = '''
SELECT
    field_1,
    field_2
FROM
    test
'''

# print(sql)
def get_sql_field():
    str_list = sql.strip().split('SELECT')[1].split('FROM')[0].split(',')
    field_list = []
    for field in str_list:
        field_list.append(field.strip())
    return field_list

if __name__ == '__main__':
    get_sql_field()
