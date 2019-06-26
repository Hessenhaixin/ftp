#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/30 17:49
# @Author  : Hessen
# @Site    : 
# @File    : client.py
# @Software: PyCharm

import socket
import struct
import json
import os
import hashlib
from conf import setting
from conf import data_deal


class Myclient:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    max_packet_size = 8192

    def __init__(self, server_address, userdata):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.username = userdata['username']
        self.user_data = userdata
        self.user_path = os.path.join(setting.user_dir_path, self.username)
        self.fuc = ['get_server_file', 'set_server_dir', 'get_myfile', 'get xx.jpg',
                    'put xxx.jpg', 'get_my_space']
        try:
            self.client_connect()
        except Exception:
            self.client_close()
            raise

    def client_connect(self):
        self.socket.connect(self.server_address)

    def client_close(self):
        self.socket.close()

    def client_send(self, msg):
        self.socket.send(msg)

    def client_recv(self, msg):
        return self.socket.recv(msg)

    def run(self):
        print('用户可执行命令：')
        for i in self.fuc:
            print(i)
        while True:
            cmd = input('>>:').strip()
            if not cmd: continue
            cmds = cmd.split()  # [get,11.jgp]
            if hasattr(self, cmds[0]):
                func = getattr(self, cmds[0])
                self.client_send(cmd.encode('utf-8'))
                func(cmds)
            else:
                print('输入错误')

    def get_server_file(self, args):
        """
        获取服务端文件
        :param args:
        :return:
        """
        res = self.client_recv(4)
        file_len = struct.unpack('i', res)[0]
        file_bytes = self.client_recv(file_len).decode('utf-8')
        file_data = json.loads(file_bytes)
        print(file_data)

    def set_server_dir(self, args):
        """
        设置服务端下载上传目录
        :param args:
        :return:
        """
        res = self.client_recv(4)
        dir_path_len = struct.unpack('i', res)[0]
        dir_path = self.client_recv(dir_path_len).decode('utf-8')
        print('当前服务器目录：', dir_path)
        server_path = input('输入需要修改的工作目录：').strip()
        server_path_bytes = server_path.encode('utf-8')
        self.client_send(struct.pack('i', len(server_path_bytes)))
        self.client_send(server_path_bytes)
        if self.client_recv(1024).decode('utf-8') == 'wrong':
            print('目录设置不成功')
        else:
            print('目录设置成功')

    def get_myfile(self, args):
        """
        获取用户文件

        """
        print(os.listdir(self.user_path))

    def get_my_space(self, args):
        """
        获取用户剩余空间

        """
        self.user_data = data_deal.loaddata(self.username)
        print(self.user_data['space'])

    def get(self, args):
        """
        从服务端下载文件
        :param args:文件名

        """
        if len(args) != 2:
            return
        res = self.client_recv(4)
        header_bytes_len = struct.unpack('i', res)[0]
        header_bytes = self.client_recv(header_bytes_len).decode('utf-8')
        header_dic = json.loads(header_bytes)
        print(header_dic)
        total_size = header_dic['file_size']
        file_name = header_dic['file_name']
        md5_data = header_dic['md5']
        file_status = header_dic['file_status']
        file_path = r'%s\%s' % (self.user_path, file_name)
        if file_status:
            with open(file_path, 'wb') as f:
                now_size = 0
                while now_size < total_size:
                    data = self.socket.recv(1024)
                    now_size = now_size + len(data)
                    f.write(data)
                    print('正在写文件---总大小%s,已下载%s' % (total_size, now_size))
                    if now_size == total_size:
                        print('恭喜你！下载完成！')
            with open(file_path, 'rb') as f:
                print('校验中····')
                data = f.read()
                md5_now_data = hashlib.md5(data).hexdigest()
                if md5_data == md5_now_data:
                    print('文件校验成功')
                else:
                    print('文件传输失败')
        else:
            print('文件不存在')

    def put(self, args):
        """从客户端上传文件到服务端"""
        if len(args) != 2:
            return
        file_name = args[1]
        file_path = r'%s\%s' % (self.user_path, file_name)
        self.user_data = data_deal.loaddata(self.username)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
                header_dic = {
                        'file_name': file_name,
                        'file_size': os.path.getsize(file_path),
                        'md5': hashlib.md5(data).hexdigest(),
                        'file_status': True,
                        'user_data': self.user_data
                        }
            if header_dic['file_size'] > self.user_data['space']:
                print('空间不足')
                header_dic['file_status'] = False
        else:
            print('文件不存在')
            header_dic = {
                'file_name': file_name,
                'file_size': 0,
                'file_status': False,
                'md5': None,
                'user_data': None
                }
        print(header_dic)
        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')
        res = struct.pack('i', len(header_bytes))
        self.client_send(res)
        self.client_send(header_bytes)
        if header_dic['file_status']:
            # 读取文件，并把文件内容发到客户端
            mess = self.client_recv(4)
            file_len = struct.unpack('i', mess)[0]
            filejson = self.client_recv(file_len).decode('utf-8')
            files = json.loads(filejson)
            file_rec_sizes = files['file_size']
            print(file_rec_sizes)
            if file_rec_sizes and file_rec_sizes < header_dic['file_size']:
                choose = input('是否需要断点续传：y需要，其他覆盖').strip()
                if choose == 'y' or choose == 'Y':
                    self.client_send('Y'.encode('utf-8'))
                else:
                    self.client_send('N'.encode('utf-8'))
                    file_rec_sizes = 0
            else:
                self.client_send('N'.encode('utf-8'))
                file_rec_sizes = 0
            with open(file_path, 'rb') as f:
                total_size = header_dic['file_size']
                send_size = 0
                status = False
                if file_rec_sizes:
                    for line in f:
                            send_size = send_size + len(line)
                            if status:
                                self.client_send(line)
                                print(send_size)
                                print('文件上传中······%.2f' % ((send_size / total_size) * 100))
                            if send_size == file_rec_sizes:
                                status = True

                else:
                    for line in f:
                            send_size = send_size + len(line)
                            self.client_send(line)
                            print(send_size)
                            print('文件上传中······%.2f' % ((send_size/total_size)*100))
            if self.client_recv(1024).decode('utf-8') == 'ok':
                print('文件上传成功')
            else:
                print('文件上传失败')
