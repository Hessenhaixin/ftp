#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/5/30 16:53
# @Author  : Hessen
# @Site    : 
# @File    : server.py
# @Software: PyCharm

import socket
import struct
import json
import os
from conf import setting
import hashlib
from conf import data_deal

class Myserver:
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    max_packet_size = 8192

    def __init__(self, server_address):
        self.server_address = server_address
        self.socket = socket.socket(self.address_family,
                                    self.socket_type)
        self.share_addr = setting.server_sharepath

        try:
            self.server_bind()
            self.server_listen()
        except Exception:
            self.server_close()
            raise

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def server_listen(self):
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        self.socket.close()

    def server_accept(self):
        return self.socket.accept()

    def run(self):
        while True:  # 链接循环
            conn, client_addr = self.server_accept()
            print(conn)
            while True:  # 通信循环
                try:
                    # 接收命令
                    cmd = conn.recv(self.max_packet_size)
                    if not cmd: break
                    print(cmd)  # b'get a.txt'
                    # 解析命令
                    cmds = cmd.decode('utf-8').split()  # [get,11.jgp]
                    if hasattr(self, cmds[0]):
                        func = getattr(self, cmds[0])
                        func(cmds, conn)
                except Exception:
                    break
            conn.close()

    def get(self, args, conn):
        if len(args) != 2:
            return
        file_name = args[1]
        share_path = r'%s\%s' % (self.share_addr, file_name)
        if os.path.isfile(share_path):
            with open(share_path, 'rb') as f:
                data = f.read()
                header_dic = {
                    'file_name': file_name,
                    'file_size': os.path.getsize(share_path),
                    'file_status': True,
                    'md5': hashlib.md5(data).hexdigest(),
                }
        else:
            print('文件不存在')
            header_dic = {
                'file_name': file_name,
                'file_size': 0,
                'file_status': False,
                'md5': None
            }
        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')
        res = struct.pack('i', len(header_bytes))
        conn.send(res)
        conn.send(header_bytes)
        if header_dic['file_status']:
            # 读取文件，并把文件内容发到客户端
            with open(share_path, 'rb') as f:
                for line in f:
                    conn.send(line)

    def put(self, args, conn):
        if len(args) != 2:
            return
        res = conn.recv(4)
        header_bytes_len = struct.unpack('i', res)[0]
        header_bytes = conn.recv(header_bytes_len).decode('utf-8')
        header_dic = json.loads(header_bytes)
        print(header_dic)
        total_size = header_dic['file_size']
        file_name = header_dic['file_name']
        md5_data = header_dic['md5']
        file_status = header_dic['file_status']
        user_data = header_dic['user_data']
        if total_size > user_data['space']:
            print('空间不足')
            return
        if file_status:
            file_path = r'%s\%s' % (self.share_addr, file_name)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
            else:
                file_size = 0
            print(file_size)
            files = {'file_size': file_size}
            file_json = json.dumps(files)
            file_bytes = file_json.encode('utf-8')
            res = struct.pack('l', len(file_bytes))
            conn.send(res)
            conn.send(file_bytes)
            choose = conn.recv(1).decode('utf-8')
            if choose == 'Y':
                now_size = file_size
                f = open(file_path, 'rb+')
            else:
                now_size = 0
                f = open(file_path, 'wb')
            f.seek(now_size)
            while now_size < total_size:
                data = conn.recv(1024)
                if not data:
                    break
                now_size = now_size + len(data)
                f.write(data)
                print('正在写文件---总大小%s,已上传%s' % (total_size, now_size))
                if now_size == total_size:
                    print('恭喜你！上传完成！')
                    user_data['space'] = user_data['space'] - getfilesize(self.share_addr)
            f.close()
            with open(file_path, 'rb') as f:
                print('校验中····')
                data = f.read()
                md5_now_data = hashlib.md5(data).hexdigest()
                if md5_data == md5_now_data:
                    print('文件校验成功')
                    data_deal.updata(user_data)
                    conn.send('ok'.encode('utf-8'))
                else:
                    print('文件校验失败')
                    conn.send('wrong'.encode('utf-8'))
                    os.remove(file_path)

    def set_server_dir(self, args, conn):
        share_addr_bytes = self.share_addr.encode('utf-8')
        conn.send(struct.pack('i', len(share_addr_bytes)))
        conn.send(share_addr_bytes)
        server_path_len = struct.unpack('i', conn.recv(4))[0]
        print(server_path_len)
        server_path = conn.recv(server_path_len).decode('utf-8')
        print(server_path)
        if os.path.isdir(server_path):
            self.share_addr = server_path
            conn.send('ok'.encode('utf-8'))
        else:
            print('目录不存在')
            conn.send('wrong'.encode('utf-8'))

    def get_server_file(self, args, conn):
        data = os.listdir(self.share_addr)
        data_json = json.dumps(data)
        data_bytes = data_json.encode('utf-8')
        conn.send(struct.pack('i', len(data_bytes)))
        conn.send(data_bytes)


def getfilesize(filepath, size=0):
        for root, dirs, files in os.walk(filepath):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size
