#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:wuqianfei
# datetime:2020/9/8 11:47 上午
# software: PyCharm
class ModebusModule:
    def __init__(self, length):
        self.modbusStorage = []
        for i in range(length):
            self.modbusStorage.append('0000')

    def setValueByAddress(self, addr, value):
        """
        设置寄存器值
        :param addr: int 地址
        :param value: 16进制数字符串 设置的值
        """
        try:
            self.modbusStorage[addr]=value
        except:
            print('超出范围')

    def getValueByAddress(self, addr):
        """
        根据寄存器地址返回值
        :param addr: int 地址
        :return: 值 16进制数字符串
        """
        try:
            return self.modbusStorage[addr]
        except:
            print('超出范围')