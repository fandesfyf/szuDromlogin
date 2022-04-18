import os.path
import subprocess
import sys
import time
import urllib.request
from urllib import parse
import base64

us = pw = None
tik = 0
headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Connection': 'keep-alive',
    'Host': 'drcom.szu.edu.cn',
    'Origin': 'https://drcom.szu.edu.cn',
    'Referer': 'https://drcom.szu.edu.cn/a70.htm'
}
logout_headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
    'Connection': 'keep-alive',
    'Host': 'drcom.szu.edu.cn',
    'Origin': 'https://drcom.szu.edu.cn',
    'Referer': 'https://drcom.szu.edu.cn/F.htm'
}
p = os.path.join(os.path.split(sys.argv[0])[0], "info.ini")
tp = os.path.join(os.path.split(sys.argv[0])[0], "填入账号密码重新运行.txt")


def logwrite(s, ln="./log.txt"):
    size = os.path.getsize(ln) if os.path.exists(ln) else 0
    with open(ln, mode='a' if size < 1024 * 1024 else 'w', encoding='utf-8') as log:
        log.write("{} ".format(time.strftime("%d/%m/%Y %H:%M:%S")) + s + "\n")
        print(s)


def encodes(s):
    return base64.b64encode(s.encode())


def tips():
    logwrite("没有密码文件")
    with open(tp, "w", encoding="utf-8") as f:
        f.write("#账号放这里(第一行)\n#密码放这里(第二行)")
    sys.exit()


def decode_pw():
    global us, pw
    with open(p, "r") as rf:
        us, pw = base64.b64decode(rf.read().encode()).decode("utf-8").split("#")
    if not us or not pw:
        logwrite("密码无效")
        os.remove(p)
        tips()


if not os.path.exists(p) and not os.path.exists(tp):
    tips()
if os.path.exists(tp):
    with open(tp, "r", encoding="utf-8") as f:
        us, pw = [i.split("#")[0].strip(" ") for i in f.read().split()]
        print(us, pw)
        with open(p, "wb") as tf:
            ec = encodes(us + "#" + pw)
            print(ec)
            tf.write(ec)
    os.remove(tp)
decode_pw()

data = {
    'DDDDD': us,  # 账号
    'upass': pw,  # 密码
    'R1': '0',
    'R2': '',
    'R6': '0',
    'para': '00',
    '0MKKey': '123456'
}
data = bytes(parse.urlencode(data), encoding='utf8')


def ping(url="ping www.baidu.com -w 1"):
    ping = subprocess.Popen(url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    log = ping.stdout.readline()

    while log:
        out = log.decode("gbk")
        # print(out)
        if "100%" in out:
            ping.terminate()
            return 0
        log = ping.stdout.readline()
    return 1


def login():
    try:
        response = urllib.request.urlopen(
            urllib.request.Request(url='https://drcom.szu.edu.cn/a70.htm', headers=headers, data=data,
                                   method='POST'))
        if response.reason == 'OK':
            body = response.read().decode('gb2312')
            if body.find('成功') > 0:
                print('登陆成功！')
                logwrite('登陆成功')
                return 1
            else:
                print('登陆失败，重试......')
                logwrite('登陆失败,正在重试......')
        else:
            print('无响应,正在重试......')
    except:
        logwrite("loginfail")
    return 0


def check_netname(name="SZU_WLAN"):
    try:
        netcheck = subprocess.Popen("netsh WLAN show interfaces", shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        netcheck.stdin.close()
        netcheck.wait(1)
        lgg = netcheck.stdout.read().decode("gbk")
        if name in lgg:
            print("状态:已连接", name)
            return True
        logwrite("未连接 {}\n".format(name))
        print("未连接", name)
    except:
        logwrite(str(sys.exc_info()) + "checkname fail\n")
    return False


def connect():
    logwrite('电脑开机，脚本开始运行。')
    try:
        login()
        logwrite("首次登录\n")
    except:
        print(sys.exc_info())
    chance = 1
    while 1:
        print("check")
        try:
            if not check_netname():
                time.sleep(1)
                # logwrite('wifi名不对')
                continue
            # 检测是否在线
            if not ping():
                logwrite('重新登录')
                login()
        except Exception:
            print(sys.exc_info())
            logwrite('异常' + str(sys.exc_info()))
        time.sleep(1)
        # logwrite('循环中')
    logwrite('退出')


def disconnect():
    response = urllib.request.urlopen(
        urllib.request.Request(url='https://drcom.szu.edu.cn/F.htm', headers=logout_headers,
                               method='GET'))
    if response.reason == 'OK':
        logwrite("注销成功")
    else:
        logwrite("注销失败")


print(sys.argv)
connect()
