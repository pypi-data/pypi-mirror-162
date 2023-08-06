# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           header_pretty.py
   Description:    请求头格式化
   Author:        
   Create Date:    2020/04/30
-------------------------------------------------
   Modify:
                   2020/04/30:
-------------------------------------------------
"""
import json


def header_pretty(headers):

    # 去除参数头尾的空格并按换行符分割
    headers = headers.strip().split('\n')

    # 使用字典生成式将参数切片重组，并去掉空格，处理带协议头中的://
    headers = {x.split(':')[0].strip(): ("".join(x.split(':')[1:])).strip().replace('//', "://") for x in headers}

    # 使用json模块将字典转化成json格式打印出来
    new_headers = json.dumps(headers, indent=1)
    # new_headers = headers
    return json.loads(new_headers)


if __name__ == '__main__':
    headers = """
content-type: application/x-www-form-urlencoded; charset=UTF-8
cookie: abcdefghijklmnopqrst
dnt: 1
if-modified-since: Thu, 01 Jan 1970 00:00:00 GMT
origin: https://example.com
referer: https://example.com/hotel/shanghai2
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36
    """
    header = header_pretty(headers)
    print(header)