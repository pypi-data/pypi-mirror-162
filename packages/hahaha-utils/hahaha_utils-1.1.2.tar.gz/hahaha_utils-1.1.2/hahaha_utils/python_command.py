import subprocess

while True:
    try:
        cmd = input("#: ")
        if 'cd ' in cmd:
            cmd = input(cmd.split('cd ')[-1] + '>')
        (status, return_data) = subprocess.getstatusoutput(cmd)
        for i in return_data.split('\\n'):
            print(i)
    except:
        pass
