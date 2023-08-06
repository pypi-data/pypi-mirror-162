# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           baidu_ocr.py
   Description:
   Author:        
   Create Date:    2020/05/03
-------------------------------------------------
   Modify:
                   2020/05/03:
-------------------------------------------------
"""
from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '19707944'
API_KEY = 'qZGpPNQwD7pglY8Epkk5sLff'
SECRET_KEY = '3oGp9iDCVTrlGvkqHG9QXfkGkWoATSXd'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
print(client)

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content("./asdf.png")

""" 调用通用文字识别（高精度版） """
client.basicAccurate(image)

""" 如果有可选参数 """
options = {}
# options["detect_direction"] = "true"
# options["probability"] = "true"

""" 带参数调用通用文字识别（高精度版） """
a = client.basicAccurate(image, options)
print(a)


# """ 读取图片 """
# def get_file_content(filePath):
#     with open(filePath, 'rb') as fp:
#         return fp.read()
#
# image = get_file_content("./dsfs.png")
#
# """ 调用通用文字识别, 图片参数为本地图片 """
# client.basicGeneral(image)
#
# """ 如果有可选参数 """
# options = {}
# # options["language_type"] = "CHN_ENG"
# # options["detect_direction"] = "true"
# # options["detect_language"] = "true"
# # options["probability"] = "true"
#
# """ 带参数调用通用文字识别, 图片参数为本地图片 """
# a = client.basicGeneral(image, options)
#
# # url = "https//www.x.com/sample.jpg"
# #
# # """ 调用通用文字识别, 图片参数为远程url图片 """
# # client.basicGeneralUrl(url)
# #
# # """ 如果有可选参数 """
# # options = {}
# # options["language_type"] = "CHN_ENG"
# # options["detect_direction"] = "true"
# # options["detect_language"] = "true"
# # options["probability"] = "true"
# #
# # """ 带参数调用通用文字识别, 图片参数为远程url图片 """
# # a = client.basicGeneralUrl(image, options)
# print(a)
