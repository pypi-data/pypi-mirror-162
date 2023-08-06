#! python3
# bulletPointAdder.py
# 复制几行文字， 运行该脚本， 打印结果： 在每行前添加*号
import pyperclip
import time
import datetime

temp = ''
while True:
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = pyperclip.paste() # 提取剪切板的文字
    if text == temp:
        pass
    else:
        print('[' + now_time + ']', '复制内容为:', text)

#lines = text.split('\n') # 按每行拆分为列表
#for i in range(len(lines)):
#    lines[i] = '* ' + lines[i] #每个列表中之前加*
#text = '\n'.join(lines) # 按每行进行列表合并
#text='DannyWU'
#pyperclip.copy(text) # 复制到剪切板中
#print('已将剪切板每行文字前添加* ')
    temp = text
