#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/31 10:07
# @Author  : Hessen
# @Site    : 
# @File    : data_deal.py
# @Software: PyCharm
from conf import setting
import os
import json
user_dir = r'%s\user_dir' % setting.DB_PATH
data_path = r'%s\db' % setting.DB_PATH


def updata(userdata):
    """
    上传用户数据
    :param userdata:
    :return:
    """
    user_path = os.path.join(user_dir, userdata['username'])
    if not os.path.isdir(user_path):
        os.mkdir(user_path)
    with open(os.path.join(data_path, '%s.json' % userdata['username']), 'w') as f:
        json.dump(userdata, f)


def loaddata(username):
    """
    下载用户数据
    :param username:
    :return:
    """
    user_path = os.path.join(data_path, '%s.json' % username)
    if os.path.isfile(user_path):
        with open(os.path.join(data_path, '%s.json' % username), 'r') as f:
            userdata = json.load(f)
            return userdata
    else:
        print('用户不存在')
        return None