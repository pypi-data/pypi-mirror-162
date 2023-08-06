# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           file_handler.py
   Description:
   Author:
   Create Date:    2020/06/23
-------------------------------------------------
   Modify:
                   2020/06/23:
-------------------------------------------------
"""
from loguru import logger as file_log
import pandas as pd
from settings import LOG_DIR

class FileHandler(object):

    def __init__(self):
        file_log.add('{}/file_handle.log'.format(LOG_DIR), encoding='utf-8')

    def read_from_csv(self, file_path, *args, **kwargs):
        """

        :param file_path:
        :param args:
        :param kwargs:
        :return:
        """
        self.file_content = None
        try:
            self.file_content = pd.read_csv(file_path, **kwargs)
        except Exception as e:
            file_log.error('没有此文件: {}'.format(file_path))
        return self.file_content

    @file_log.catch()
    def read_from_excel(self, file_path, *args, **kwargs):
        """

        :param file_path:
        :param args:
        :param kwargs:
        :return:
        """

        self.file_content = None
        try:
            self.file_content = pd.read_excel(file_path, **kwargs)
        except Exception as e:
            file_log.error('没有此文件: {}'.format(file_path))
        return self.file_content

    def write_to_excel(self, file_path, data_list, columns, *args, **kwargs):
        """

        :param file_path:
        :param data_list:
        :param columns:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            df = pd.DataFrame(data_list, columns=columns)
            df.to_excel(file_path, index=False)
            file_log.info('写入excel文件成功！')
            return 1
        except Exception as e:
            file_log.error('写入 {} 失败'.format(file_path) + '错误信息: {}'.format(str(e)))
            return 0

    def write_to_csv(self, file_path, data_list, columns, mode='w', header=True, *args, **kwargs):
        """

        :param file_path:
        :param data_list:
        :param columns:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            df = pd.DataFrame(data_list, columns=columns)
            df.to_csv(file_path, index=False, mode=mode, header=header)
            # file_log.info('写入csv文件成功！')
            return 1
        except Exception as e:
            if str(columns) == "['列1', '列2', Ellipsis]":
                file_log.error('写入 {} 失败.'.format(file_path) + ' 错误信息: 未更改task_settings.py内的columns默认配置，请前往修改！')
            else:
                file_log.error('写入 {} 失败.'.format(file_path) + ' 错误信息: {}'.format(str(e)))
            return 0

    def split_csv(self, file_path, sub_file_number, sub_file_row, sub_file_type='csv'):
        """
        :param file_path: origin big csv file
        :param sub_file_number: number of sub file number
        :param sub_file_row: row number of per sub file
        :param sub_file_type: sub file type
        :return:
        """
        file_path = file_path.replace('\\', '/')
        # 打开文件
        data = pd.read_csv(file_path, low_memory=False)


        print('正在分割...')
        for i in range(sub_file_number):
            save_data = data.iloc[i * sub_file_row + 1: (i + 1) * sub_file_row + 1]
            if sub_file_type == 'excel':
                file_name = file_path.replace('.csv', '_') + str(i) + '_.xlsx'
                save_data.to_excel(file_name, index=False)
            elif sub_file_type == 'csv':
                file_name = file_path.replace('.csv', '_') + str(i) + '_.csv'
                save_data.to_csv(file_name, index=False)
            else:
                print('类型出错!')
        print('分割完成，共 ' + sub_file_number + ' 个子文件!')



if __name__ == '__main__':
    eh = FileHandler()
    # print(file_content)
    eh.split_csv("data.csv", 3, 600000, sub_file_type='excel')