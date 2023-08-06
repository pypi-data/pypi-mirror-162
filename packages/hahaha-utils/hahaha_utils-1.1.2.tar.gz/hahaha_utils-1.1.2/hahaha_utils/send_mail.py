# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           send_mail.py
   Description:
   Author:        
   Create Date:    2020/08/07
-------------------------------------------------
   Modify:
                   2020/08/07:
-------------------------------------------------
"""
import yagmail


# 邮件发送
def send_email(contents):
    """
    发送通知邮箱
    :param contents: 邮件内容
    :return: None
    """
    # 链接邮箱服务器
    yag = yagmail.SMTP(user="user@example", password="gmail", host='gmail.com', port=465, smtp_ssl=True)
    # 邮箱正文
    # contents = 'This is the body, and here is just text '
    # 发送邮件

    receiver = ['gamil@gmail.com']
    yag.send(receiver, 'test', contents)
    yag.send()
    print('发送成功！')




if __name__ == '__main__':
    send_email('nihao')