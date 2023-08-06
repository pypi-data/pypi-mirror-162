#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022年8月6日 21:37
# @Author  : Lumo
# @Site    : Home
# @File    : downloadBingImg.py
# @Software: PyCharm


import os
import time
from ctypes import windll

import requests
from lumopypackage import userAgent
from lumopypackage import userPath


def downloadBingImg(select=False):
    '''
    该函数会爬取Bing的图片设置成壁纸。
    目前只能用在windows品台下。
    select默认为False的时候不会保存图片，select为True时图片会保存在当前登录用户目录下的\图片\Bing目录。
    '''

    headers = {
        'User-Agent': userAgent()
    }
    # 拼接url
    url = f'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1'

    # 爬取Bing每日图片的json数据
    response = requests.get(url, headers=headers)

    # 处理爬到的json数据
    content = response.json()['images'][0]
    imgUrl = f'https://cn.bing.com' + content['url']
    title = content['title'].strip('?').strip('”').strip('“')
    startdate = content['startdate']

    # 拼接图片名字
    imgName = startdate + title + '.jpg'

    # 判断存图片的路径
    if select:
        # 获取当前登录用户目录下图片文件夹的路径
        homePath = userPath('图片') + f'Bing'

        # 创建Bing文件夹
        if not os.path.exists(homePath):
            os.makedirs(homePath)
        imgPath = homePath + '\\' + imgName

    else:
        # 从系统变量获取temp路径
        temp = os.environ.get('TEMP')

        imgPath = temp + '\\' + imgName

    # 下载图片
    img = requests.get(imgUrl, headers=headers)
    with open(imgPath, 'wb') as f:
        f.write(img.content)

    # 设置壁纸
    windll.user32.SystemParametersInfoW(20, 0, imgPath, 0)

    # 删除下载的图片
    if not select:
        time.sleep(0.1)
        os.remove(imgPath)

    return


if __name__ == '__main__':
    downloadBingImg()
    pass
