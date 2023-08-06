# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           receive_mail.py
   Description:
   Author:        
   Create Date:    2020/12/04
-------------------------------------------------
   Modify:
                   2020/12/04:
-------------------------------------------------
"""
from mysql.connector import connect
connect()
from datetime import datetime
import imaplib
import email
import time
import quopri
from lxml import etree
from hahaha_utils.mail_date_list import MAIL_DATE_LIST


def aliyun_mail_to_qy_wechat(imapb, flag):
    # while True:
    now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    # try:
    t = imapb.select('INBOX')
    typ, data = imapb.search(None, 'ALL')
    all_mails = data[0].decode().split(' ')
    if flag < len(all_mails):
        if flag == 0:
            v_number = 500
        else:
            v_number = len(all_mails) - flag
        flag = len(all_mails)
        print(len(all_mails))

        # 获取最近十封邮件
        recent_mails = all_mails[len(all_mails) - v_number:]
        # 按邮件的索引倒序
        recent_mails.sort(reverse=True)

        for mailNum in recent_mails:
            # print(1111111111111111, mailNum)
            typ, msg_data = imapb.fetch(mailNum, '(RFC822)')
            # print(typ, msg_data)
            response_part = msg_data[0][1]

            # 获取一封邮件的全部内容
            mail_all_content = email.message_from_string(response_part.decode('utf-8'))

            mail_subject = quopri.decodestring(mail_all_content['Subject']).decode().replace('=?utf-8?q?','').replace('=?UTF-8?Q?','').replace('_',' ').replace('?','').replace('=UTF-8q', '').replace('= =UTF-8q', '').replace(' =UTF-8q', '').replace('= ', '')  # .replace('?=', '').replace('=?UTF-8?q?', '').replace('=?UTF-8?q', '')
            mail_from = mail_all_content['From']
            mail_to = mail_all_content['To']

            if '+' in  mail_all_content['Date']:
                mail_date_text = mail_all_content['Date'].split('+')[0].strip()  # print(mail_all_content)
                a = datetime.strptime(mail_date_text, '%a, %d %b %Y %H:%M:%S')
                mail_date = datetime.strftime(a, '%Y-%m-%d %H:%M:%S')
            else:
                mail_date = mail_all_content['Date']

            content_transfer_encoding = mail_all_content['Content-Transfer-Encoding']
            print(now, '**subject: ', mail_subject)
            # if 'monitor.alibabacloud.com' in mail_from and 'Alarm' in mail_subject:
            if 'monitor.alibabacloud.com' in mail_from and ('Alarm' in mail_subject or 'Monitor' in mail_subject) and mail_date not in MAIL_DATE_LIST:


                # print('现在是：', now)
                print(
                    '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                print('**subject: ', mail_subject)
                print('**mail_from', mail_from)
                print('**mail_to', mail_to)
                print('**mail_date', mail_date)
                print('**content_transfer_encoding', content_transfer_encoding)
                payload = mail_all_content.get_payload()
                # print(payload)
                content = payload[0]

                mail_html = quopri.decodestring(str(content)).decode()
                print('##############################################################################')
                # print(mail_html)
                html = etree.HTML(mail_html)
                with open(str(mail_date).replace(':', '').replace('+','').replace('(CST)','').replace(',','')+'.html', 'w', encoding='utf-8')as f:
                    f.write(str(mail_html).split('quoted-printable')[-1])
                    f.close()
                td_s = html.xpath('//tr[3]//td/text()')
                a_s = html.xpath('//tr[3]//a')
                # print(td_s)
                send_text = ''
                for td in td_s[:-1]:
                    # if 'Alibaba' in td:
                    td_text = td.strip()
                    if td_text != '':
                        # print(td_text)
                        send_text = send_text + td_text + '\n'
                for a in a_s:
                    a_text = a.xpath('./text()')[0].strip() + '\n'
                    a_href = a.xpath('./@href')[0].strip() + '\n'
                    send_text = send_text + a_text + a_href
                print('1111111111111111111111111111111111111111')
                print(send_text)
                MAIL_DATE_LIST.append(mail_date)
                print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', MAIL_DATE_LIST)
        with open('mail_date_list.py', 'w')as f:
            f.write('MAIL_DATE_LIST = {}'.format(MAIL_DATE_LIST))
            f.close()
        print('###########################################################################################')
        time.sleep(1)
    else:
        print('现在是：', now)
        print('目前没有新的邮件!')
        print('###########################################################################################')
        time.sleep(1)

    return flag


if __name__ == '__main__':

    flag = 0
    imapb = imaplib.IMAP4_SSL('exmail.qq.com', port=993)
    imapb.login('user@example.id', 'example')
    while True:
        try:
            flag_1 = aliyun_mail_to_qy_wechat(imapb, flag)
            flag = flag_1
            print(flag)
        except Exception as e:
            print('错误信息', e)
            now_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            try:
                imapb = imaplib.IMAP4_SSL('exmail.qq.com', port=993)
                imapb.login('user@example.id', 'example')
                print('重新登陆成功！')
                with open('login_success_log.log', 'a', encoding='utf-8') as f:
                    f.write(now_time + ' 重新登陆成功！\n')
                    f.close()
            except Exception as e:
                print('错误信息', e)
                print(now_time + '重新登陆失败！')
                with open('login_fail_log.log', 'a', encoding='utf-8') as f:
                    f.write(now_time + ' 重新登陆失败！\n')
                    f.close()
                pass
