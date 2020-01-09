# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import json
import time
import requests
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad


def Md5(str):
    # 创建md5对象
    m = hashlib.md5()
    b = str.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    # print('MD5加密后为 ：' + str_md5)
    return str_md5


headers = {
    'User-Agent': 'Mozilla/5.0',
    "Content-Type": "application/json",
}

# 登陆授权请求业务参数
def get_dlmes():
    t = datetime.datetime.now()
    time1 = t.strftime("%Y%m%d")
    time2 = str(t.time()).replace(':', '').replace('.', '')[:10]
    time3 = time1 + time2  # 202001020938290362
    # time_now = time.time()
    # time_local = time.localtime(time_now)  # 格式化时间戳为本地时间
    # time_YmdHMS = time.strftime("%Y%m%d%H%M%S", time_local)  # 自定义时间格式
    # time3 = time_YmdHMS + str(time_now).split('.')[-1][:4]
    data1 = {"client": "JXGLJK_DF0A6F9B3D9A8C5A004F89D65",
             "account": "SMS_JXGLJK_5D8A6",
             "password": "JXGLJKL#F65A28A6D608BBF4C2691A8D",
             "time": time3}
    ms = data1['client'] + data1['account'] + data1['time']
    # 进行AES加密
    key = 'B09C6ABE546FCD0E'
    BLOCK_SIZE = 16
    # AES加密模式
    mode = AES.MODE_ECB
    aes = AES.new(key=key.encode('utf-8'), mode=mode)
    text = bytes(ms.encode('utf-8'))
    # 获取到加密的mac值
    p_mac = aes.encrypt(pad(text, BLOCK_SIZE))
    data1['mac'] = p_mac.hex()
    b64_data1 = base64.b64encode(str(data1).encode('utf-8')).decode('utf-8')
    return b64_data1


# 发送请求
def send_post(url, sign, param):
    data = {
        'sign': sign,
        'time': str(int(time.time() * 1000)),
        'param': param,
    }
    # factor = time + base64 + sign;
    factor = data['time'] + param + data['sign']
    mac_md5 = Md5(factor)
    data['mac'] = mac_md5
    try:
        res = requests.post(url=url, json=data)
        result = res.text
        print(data, result)
        result = json.loads(result)
    except Exception as e:
        result = {'Error': '%s' % e, 'data': '%s' % str(data)}

    finally:
        return result


# 短信请求业务参数
def send_mesage(old_version, new_version):
    data1 = {
        "batch_num": "1",
        "signature": "【四川增值税综合平台】",
        "mobiles": "18200332758;",  # (多个电话之间以分号隔开)
        "content": "检测到版本更新：新版本号：%s，更新时间:%s" % (old_version, new_version)
    }
    b64_data1 = base64.b64encode(str(data1).encode('utf-8')).decode('utf-8')
    return b64_data1

#主函数
def main(old_version, new_version):
    # 获取登陆业务参数
    dl_m = get_dlmes()
    # 获取登陆授权sign
    sign = send_post('http://server.204.hydzfp.com:8088/hy_sms/sms/login.do', '', dl_m)
    sign = eval(base64.b64decode(sign['rows']).decode('utf-8'))['sign']
    # 获取短信业务参数
    dx_m = send_mesage(old_version, new_version)
    # 发送短信
    res = send_post('http://server.204.hydzfp.com:8088/hy_sms/sms/send.do', sign, dx_m)
    return res


if __name__ == '__main__':
    s = main('4.0.02', '4.0.03')
