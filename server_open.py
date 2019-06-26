#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/31 15:48
# @Author  : Hessen
# @Site    : 
# @File    : server_open.py
# @Software: PyCharm

from servers import server

# 服务端启动程序
if __name__ == '__main__':
    server1 = server.Myserver(('127.0.0.1', 8080))  # 可以设置服务端地址
    server1.run()