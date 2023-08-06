# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           convert_pdf_table_html.py
   Description:    提取PDF文件中的表格转换为html
   Author:        
   Create Date:    2020/05/12
-------------------------------------------------
   Modify:
                   2020/05/12:
-------------------------------------------------
"""

import camelot
from urllib import parse


def convert_pdf_table_html(pdf_file_path, save_file_path, table_index=None, **kwargs):
    """

    :param pdf_file_path:
    :param save_file_path:
    :param table_index:
    :param kwargs:
    :return:
    """


    pdf_file_path = pdf_file_path.strip()

    try:
        pdf_file_path_temp = parse.unquote(pdf_file_path)
        # print(pdf_file_path)
        # 获取文件名字
        # file_name = ''
        # if '\\' in pdf_file_path_temp:
        #     file_name = pdf_file_path_temp.split('\\')[-1].replace('.' + pdf_file_path_temp.split('\\')[-1].split('.')[-1], '')
        # elif '/' in pdf_file_path_temp:
        #     file_name = pdf_file_path_temp.split('/')[-1].replace('.' + pdf_file_path_temp.split('/')[-1].split('.')[-1], '')

        if 'http' in pdf_file_path and '%' not in pdf_file_path:
            tables = camelot.read_pdf(pdf_file_path.replace(pdf_file_path.split('/')[-1], parse.quote(pdf_file_path.split('/')[-1])), flavor='stream', **kwargs)
        else:
            tables = camelot.read_pdf(pdf_file_path, flavor='stream', **kwargs)

        # 转换所有表格
        if table_index is None:
            print(len(tables))
            x = 0
            for i in tables:
                i.df.to_html(save_file_path +  str(x) + '.html')
                x += 1

        #指定表格索引
        tables[table_index].df.to_html(save_file_path + '0' + '.html')
        return 'ok'
    except Exception as e:
        print(e)
        return 'fail'


if __name__ == '__main__':
    pdf_file_path = "./pdf/test.pdf"
    save_file_path = "./pdf"
    convert_pdf_table_html(pdf_file_path, save_file_path, -1, pages='all')