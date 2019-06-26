#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/31 10:10
# @Author  : Hessen
# @Site    : 
# @File    : login_enter.py
# @Software: PyCharm
import os
from conf import data_deal
from conf import setting
import sys
from clients import client


def user_login():
    """
    用户登录
    :return:
    """
    username = input('输入账号名:').strip()
    password = input('输入密码:').strip()
    userdata = data_deal.loaddata(username)
    if userdata:
        if userdata['password'] == password:
            print('恭喜登录成功')
            clients = client.Myclient(('127.0.0.1', 8080), userdata)  # 服务端地址
            clients.run()
            return True
        else:
            print('密码不正确')
            return False


def user_register():
    """
    用户注册
    :return:
    """
    username = input('输入账号名:').strip()
    password = input('输入密码:').strip()
    user_path = os.path.join(data_deal.data_path, '%s.json' % username)
    if os.path.isfile(user_path):
        print('用户已存在')
        return False
    else:
        userdata = {'username': username, 'password': password, 'space': 200000000}  # 用户空间默认200000000bytes
        data_deal.updata(userdata)
        print('注册成功')
        return True





