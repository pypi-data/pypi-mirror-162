#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022年8月6日 21:37
# @Author  : Lumo
# @Site    : Home
# @File    : downloadBingImg.py
# @Software: PyCharm


import os
import subprocess


def userPath(path=''):
    '''
    次函数用于获取windows平台下当前登录账户的目录路径。
    '''

    # 判断是windows平台执行函数。
    if os.name == 'nt':

        # 执行终端明天通过管道获取用户目录路径。
        obj = subprocess.Popen('echo %USERPROFILE%',
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

        # 将从管道拿到的内容转成字符串类型，并去除末尾的换行符。
        if path == '视频':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Videos\\'
            return userpath
        elif path == '图片':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Pictures\\'
            return userpath
        elif path == '文档':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Documents\\'
            return userpath
        elif path == '下载':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Downloads\\'
            return userpath
        elif path == '音乐':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Music\\'
            return userpath
        elif path == '桌面':
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\Desktop\\'
            return userpath
        else:
            userpath = obj.stdout.read().decode('utf-8').strip('\n').strip('\r') + f'\\'
            return userpath

    # 判断不是windows平台提示错误。
    else:
        print('此函数只能用于windows平台')
        return '此函数只能用于windows平台'


if __name__ == '__main__':
    pass
