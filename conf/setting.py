#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/30 16:55
# @Author  : Hessen
# @Site    : 
# @File    : setting.py
# @Software: PyCharm
import os
DB_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 用户根目录
server_sharepath = r'%s\服务端\share' % DB_PATH  # 服务端下载目录
user_dir_path = r'%s\user_dir' % DB_PATH  # 用户目录
