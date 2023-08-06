# -*- coding: utf-8 -*-
import paramiko
import datetime
import time
for i in range(10000000):
    now_t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = '54.180.163.206'
    print(ip)
    port = 58252
    user = "root"
    password = "abcd1234."
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 建立连接
    ssh.connect(ip,port,user,password,timeout = 10)
    #输入linux命令
    stdin,stdout,stderr = ssh.exec_command("pwd")
    # 输出命令执行结果
    result = stdout.read()
    with open('result.txt', 'a')as f:
        f.write(ip + '---' + now_t + '--connect success--' + str(result).replace('b','').replace('\\n','').replace("'","") + '\n')
        print(str(result).replace('b','').replace('\\n',''))
    time.sleep(300)


