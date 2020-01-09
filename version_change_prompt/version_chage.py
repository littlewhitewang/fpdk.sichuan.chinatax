# -*- coding: utf-8 -*-
import base64
import datetime
import hashlib
import re
import time
import requests
from send_message import mes_main

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}


# 获取页面当前版本
def get_version():
    try:
        url = 'https://fpdk.sichuan.chinatax.gov.cn/'
        res = requests.get(url=url, headers=headers, verify=False)
        res.encoding = 'utf-8'
        # print(res.text)
        # version = '<div class=theme-popbod4><h2>增值税发票综合服务平台V4.0.03升级内容说明</h2>'
        version = re.findall('class=theme-popbod4><h2>.*?平台(.*?)升级内容说明</h2>', res.text)[0]
        # print(version)
        return version
    except:
        print('版本请求失败')


# 如果版更改调用短信接口，否则不处理
def check_version(new_version, old_version):
    if new_version != old_version:
        # 发送更新短信
        res = mes_main(old_version, new_version)
        if res['code'] == '000000':
            # 更新版本参数
            result = update_version(new_version)
        else:
            result = {'code': '2222', 'mes': '短信发送失败！检测到版本更新为：%s' % new_version, 'Error': res}
    else:
        result = {'code': '0000', 'mes': '没有更新的版本，当前版本号：%s' % old_version}
    return result


# 更新记录版本号文档
def update_version(new_version):
    try:
        current_date = datetime.datetime.now()
        print(current_date)
        txt = '版本号:' + new_version + '  更新时间:%s' % current_date + '\n'
        with open('./version_history.txt', 'a', encoding='utf-8') as f:
            f.write(txt)
        return {'code': '1111', 'mes': '发送短信成功！替换旧版本成功！新版本号%s' % new_version}
    except Exception as e:
        return {'code': '9999', 'mes': '发送短信成功，但替换旧版本失败！新版本号%s' % new_version, 'Error': e}


def main():
    # version = '3.0.03'
    t = datetime.datetime.now().hour
    while True:
        try:
            with open('./version_history.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_line = lines[-1]  # 获取最后一行
                print(last_line)
            version = re.search(r'版本号:(.*?)更新时间', last_line).group(1).strip()
            new_version = get_version()
            res = check_version(new_version, version)
            print(res)
        except Exception as e:
            print({'code': '7777', 'Error': e})
        time.sleep(60 * 60)


if __name__ == '__main__':
    main()
