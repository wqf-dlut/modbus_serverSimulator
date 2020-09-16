#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:wuqianfei
# datetime:2020/9/8 11:47 上午
# software: PyCharm

import socketserver
from Modules.ModebusModule import ModebusModule
from multiprocessing import Queue
import binascii
import time


# HOST, PORT = "localhost", 2404


class ModbusBusiness(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            targetInfo = self.client_address[0] + ":" + str(self.client_address[1])
            while self.server.serverEnable[0]:
                recvData = self.request.recv(2048)
                recvHex = str(binascii.b2a_hex(recvData))[2:-1]
                if not recvData:
                    break
                self.server.showBuff.put(('rec', time.strftime("%Y-%m-%d %H:%M:%S",
                                                               time.localtime()) + " " + targetInfo + ' recv:' + recvHex))
                sendMsg = self.analysisRecv(recvHex)
                self.server.showBuff.put(('send', time.strftime("%Y-%m-%d %H:%M:%S",
                                                                time.localtime()) + " " + targetInfo + ' send:' + sendMsg))
                self.request.sendall(binascii.a2b_hex(bytes(sendMsg.encode('utf-8'))))
            self.request.close()
        except:
            print('IO出错')

    def setup(self):
        print('接收了链接')

    def finish(self):
        self.request.close()

    def analysisRecv(self, recvData):
        """
        分析数据并返回
        :param recvData:string 接收到的数据
        :return: string 发送的数据
        """
        sendData = []
        for i in range(5):
            sendData.append('')
        try:
            functionId = recvData[14:16]
            startAddr = int(recvData[16:20], 16)
            countAddr = int(recvData[20:24], 16)

            if not functionId == '10':
                sendData[0] = recvData[0:8]  # 序号+协议号
                sendData[1] = '{:04X}'.format(2 * countAddr + 3)  # 长度
                sendData[2] = recvData[12:16]  # slaveid and functionid
                # 字节数
                if 2 * countAddr > 255:
                    sendData[3] = '00'
                else:
                    sendData[3] = '{:02X}'.format(2 * countAddr)
                # 数据内容
                sendData[4] = ''
                for i in range(startAddr, startAddr + countAddr):
                    sendData[4] += self.server.storageBuff.getValueByAddress(i)
                return ''.join(sendData)
            else:
                return recvData[0:24]
        except:
            return ('ffffffff')
        pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    def __init__(self, host_port_tuple, streamhandler, storageBuff, showBuff, isEnable):
        super().__init__(host_port_tuple, streamhandler)
        self.storageBuff = storageBuff
        self.showBuff = showBuff
        self.serverEnable = isEnable


if __name__ == "__main__":
    HOST, PORT = "192.168.137.53", 5000
    storageBuff = ModebusModule(5000)
    showBuff = Queue()
    server = ThreadedTCPServer((HOST, PORT), ModbusBusiness, storageBuff, showBuff)
    server.serve_forever()
