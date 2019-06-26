#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/31 15:46
# @Author  : Hessen
# @Site    : 
# @File    : clent_entrance.py
# @Software: PyCharm
from conf import setting
from conf import login_enter
import sys
# 客户端启动程序
if __name__ == '__main__':
    sys.path.append(setting.DB_PATH)
    while True:
        choose = input('>>:登录或者注册').strip()
        if choose == '登录':
            login_enter.user_login()
        elif choose == '注册':
            login_enter.user_register()