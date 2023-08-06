# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           下载jetbrains_active_code
   Description:
   Author:        
   Create Date:    2020/09/27
-------------------------------------------------
   Modify:
                   2020/09/27:
-------------------------------------------------
"""
from zipfile import ZipFile
from requests import get
from os import remove
from time import sleep


def download_jetbrains_active_code(zip_file_name):
    d_url = 'http://idea.medeming.com/a/jihuoma2.zip'
    try:
        resp = get(d_url)
        with open(zip_file_name, 'wb')as f:
            f.write(resp.content)
            f.close()
        print()
        # print('jetbrains_active_code.zip 下载成功！')
    except Exception as e:
        print('网络错误：', e)

def read_zip_file(zip_file):
    try:
        z = ZipFile(zip_file, 'r')
        # 打印zip文件中的文件列表
        for file_name in z.namelist():
            if '2018.2' in file_name:
                content = z.read(file_name).decode()
                active_code_text = ''
                print('您的jetbrains激活码为: ')
                print()
                # print(len(active_code_text))
                # print(active_code_text)
                for i in range(50):
                    start = 150 * i
                    end = 150 * (i + 1)
                    # print(start, end)
                    if content[start: end].strip() != '':
                        active_code_text = active_code_text + content[start: end].strip() + '\n'
                print(active_code_text.strip())
        z.close()
        remove(zip_file)
        print()
        print('祝您生活愉快！')

    except Exception as e:
        print('打开压缩包出现错误：', e)

if __name__ == '__main__':
    zip_file_name = 'jetbrains_active_code.zip'
    download_jetbrains_active_code(zip_file_name)
    read_zip_file(zip_file_name)
    sleep(1000000)