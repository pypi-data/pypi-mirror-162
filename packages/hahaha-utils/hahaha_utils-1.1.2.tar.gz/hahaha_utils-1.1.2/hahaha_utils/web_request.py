# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           web_request.py
   Description:    请求页面
   Author:
   Create Date:    2020/03/24
-------------------------------------------------
   Modify:
                   2020/03/24:
-------------------------------------------------
"""

from requests.models import Response
import requests
import random
import time
from json import dumps
from hahaha_utils.log_handler import LogHandler
from lxml import etree
from bs4 import BeautifulSoup

class WebRequest(object):
    def __init__(self, *args, **kwargs):
        # pass
        self.log = LogHandler('web_request')
        self.response = None

    @property
    def user_agent(self):
        """
        return an User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def header(self):
        """
        basic header
        :return:
        """
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}

    def get(self, url, header=None, retry_time=5, timeout=30,
            retry_flag=list(), retry_interval=5, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time when network error
        :param timeout: network timeout
        :param retry_flag: if retry_flag in content. do retry
        :param retry_interval: retry interval(second)
        :param args:
        :param kwargs:
        :return:
        """
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)
        while True:
            try:
                self.response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
                if any(f in self.response.content for f in retry_flag):
                    raise Exception
                return self.response
            except Exception as e:
                self.log.info('requests get请求错误: ' + str(e) + ' ' + url)
                retry_time -= 1
                if retry_time <= 0:
                    # 多次请求失败
                    resp = Response()
                    # 自定义失败状态码
                    resp.status_code = 8888
                    return resp
                time.sleep(retry_interval)

    def post(self, url, header=None, data=None, retry_time=5, timeout=30,
            retry_flag=list(), retry_interval=5, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers
        :param retry_time: retry time when network error
        :param timeout: network timeout
        :param retry_flag: if retry_flag in content. do retry
        :param retry_interval: retry interval(second)
        :param args:
        :param kwargs:
        :return:
        """
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)

        try:
            if 'application/json' in header['content-type'] :
                data = dumps(data)
        except:
            try:
                if 'application/json' in header['Content-Type']:
                    data = dumps(data)
            except Exception as e:
                pass
        # print(data)
        while True:
            try:
                self.response = requests.post(url, headers=headers, data=data, timeout=timeout, **kwargs)
                if any(f in self.response.content for f in retry_flag):
                    raise Exception
                return self.response
            except Exception as e:
                self.log.info('requests post请求错误: ' + str(e) + ' ' + url)
                retry_time -= 1
                if retry_time <= 0:
                    # 多次请求失败
                    resp = Response()
                    resp.status_code = 8888
                    return resp
                time.sleep(retry_interval)

    def xpath(self):
        html = etree.HTML(self.response.text)

        return html

    def selector(self):
        soup = BeautifulSoup(self.response.text, 'lxml')

        return soup



if __name__ == '__main__':
    pass
    wr = WebRequest()
    resp = wr.get('https://www.idannywu.com')
    print(resp)
    print(wr.response.status_code)
    html = wr.xpath()
    print(html.xpath('//a/@href'))
    selector = wr.selector()
    print(selector.select('.os-login-box'))
