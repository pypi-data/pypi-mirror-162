#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022年8月6日 21:37
# @Author  : Lumo
# @Site    : Home
# @File    : downloadBingImg.py
# @Software: PyCharm

import random

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning


def userAgent():
    '''
    此函数用于获取一个随机的User-Agent。
    '''

    # 解决设置verify=False移除SSL认证时，出现InsecureRequestWarning警告
    urllib3.disable_warnings(InsecureRequestWarning)

    url = 'https://nas.lumo520.com/d/s/pogyOzEiOMoGIIvuuNFrj5DbTVrbvAA6/webapi/entry.cgi/User-Agent.csv?api=SYNO.SynologyDrive.Files&method=download&version=2&files=%5B%22id%3A701492140223544570%22%5D&force_download=true&json_error=true&c2_offload=%22allow%22&_dc=1659873587876&sharing_token=%22LJzgC06wxpkF8csQtvVyVVSYR6fQQ4GChjQpA5BHRl0L7KoD64eXUA_BDSJ9fMXaLubV4.QJe9aGDnWuoLRQhELVTK4VdtDGCN2ZnuZK3aIiL385.ercxcRG759T21bZVHlJ0RdCWON2Sl4R07Bfy0lBtvLXT0J0vn715hsYwCXlwgY4HBaDJW.dsN1dwgsaZHa.Ov4ul4eXRye0wAH9kz0rqtvO9ar5C69O3Y9Py6nyvAa.1qL0973v%22'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'
    }

    # 获取User-Agent数据
    res = requests.get(url, headers=headers, verify=False)

    # 整理User-Agent数据
    line = res.text.split('\r\n')
    num = len(line)
    return f"'" + line[random.randrange(0, num)].strip('"').strip("'") + "'"


if __name__ == '__main__':
    pass
