#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:wuqianfei
# datetime:2020/9/8 1:46 下午
# software: PyCharm
import socketserver
import sys
import json
import time

from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5 import QtCore
from PyQt5.Qt import QThread
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QDateTime, QTimer
from Views.mainUi import Ui_Form
from Modules.ModebusModule import ModebusModule
from Business.ModbusBusiness import ModbusBusiness, ThreadedTCPServer
from multiprocessing import Queue


class MyMainWindow(QMainWindow, Ui_Form):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('modbusServer')
        self.storageBuff = ModebusModule(5000)
        self.showBuff = Queue()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshTable)
        self.timer.start(500)
        self.textBrowserEnable = True
        self.server = None
        self.serverEnable = [False]
        self.pushButton_refreshDisable.clicked.connect(lambda: self.changeRefresh(False))
        self.pushButton_refreshEnable.clicked.connect(lambda: self.changeRefresh(True))
        self.pushButton_clear.clicked.connect(lambda: self.clearTextBrowser())
        self.pushButton_stop.clicked.connect(self.stopServer)
        self.pushButton_start.clicked.connect(self.startServer)
        self.pushButton_SetValueAi.clicked.connect(self.setValueAi)
        self.pushButton_SetValueDi.clicked.connect(self.setValueDi)
        self.pushButton_getValue.clicked.connect(self.getValue)

    def refreshTable(self):

        if self.textBrowser.document().lineCount() > 300:
            self.clearTextBrowser()
        while not self.showBuff.empty():
            tmplist = self.showBuff.get()
            if tmplist[0] == 'error':
                tmp = "<font color=\"#FF0000\">" + tmplist[1] + "</font> "
            if tmplist[0] == 'rec':
                tmp = "<font color=\"#00868B\">" + tmplist[1] + "</font> "
            if tmplist[0] == 'send':
                tmp = "<font color=\"#483D8B\">" + tmplist[1] + "</font> "
            else:
                tmp = tmplist[1]
            if self.textBrowserEnable:
                self.textBrowser.append(tmp)
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)

    def changeRefresh(self, TrueOrFalse):
        """
        停止或正常刷新
        :param TrueOrFalse:是否刷新
        """
        self.textBrowserEnable = TrueOrFalse

    def clearTextBrowser(self):
        QApplication.processEvents()
        self.textBrowser.clear()

    def startServer(self):
        try:
            self.serverEnable[0] = True
            HOST, PORT = self.lineEdit_setIP.text(), int(self.spinBoxPortNum.value())
            self.server = ThreadedTCPServer((HOST, PORT), ModbusBusiness, self.storageBuff, self.showBuff,
                                            self.serverEnable)
            self.thread_1 = ServerFoever(self.server)  # 创建线程
            self.thread_1.start()  # 开始线程
            self.showBuff.put(
                ('sys', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' 启动服务器:' + HOST + ":" + str(PORT)))
        except:
            self.showBuff.put(('error', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' 启动失败'))

    def stopServer(self):
        try:
            self.serverEnable[0] = False
            self.thread_1.quit()
            self.showBuff.put(('sys', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' 服务已经关闭'))
        except:
            self.showBuff.put(('error', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '无启动中的服务'))

    def setValueAi(self):
        try:
            self.storageBuff.setValueByAddress(int(self.spinBoxSetValueAi.value()),
                                               '{:04X}'.format(int(self.lineEdit_setValueAi.text())))
        except:
            pass

    def setValueDi(self):
        tmp = ''
        for i in [self.checkBox_0, self.checkBox_1, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5,
                  self.checkBox_6,
                  self.checkBox_7, self.checkBox_8, self.checkBox_9, self.checkBox_10, self.checkBox_11,
                  self.checkBox_12,
                  self.checkBox_13, self.checkBox_14, self.checkBox_15]:
            if i.isChecked():
                tmp = '1' + tmp
            else:
                tmp = '0' + tmp
        try:
            self.storageBuff.setValueByAddress(int(self.spinBoxSetValueDi.value()),
                                               '{:04X}'.format(int(tmp, 2)))
            self.showBuff.put(('sys', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 寄存器 " +
                               str(self.spinBoxSetValueDi.value()) + ' 设置值成功'))
        except:
            self.showBuff.put(('sys', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 寄存器 " +
                               str(self.spinBoxSetValueDi.value()) + ' 设置值失败'))

    def getValue(self):
        try:
            QApplication.processEvents()
            self.lineEdit_getHex.clear()
            self.lineEdit_getBit.clear()
            tmpValue = self.storageBuff.getValueByAddress(int(self.spinBoxGetValue.value()))

            self.label_getHex.setText("值(hex): ")
            self.lineEdit_getHex.setText(tmpValue)

            tmpbit = '{:016b}'.format(int(tmpValue, 16))
            self.label_getBit.setText('值(bit):')
            self.lineEdit_getBit.setText(tmpbit[0:4] + " " + tmpbit[4:8] + " " + tmpbit[8:12] + " " + tmpbit[12:])

        except:
            print('获取数据失败')


class ServerFoever(QThread):  # 线程1
    def __init__(self, ParmServer):
        super().__init__()
        self.server = ParmServer

    def run(self):
        self.server.serve_forever()

    def quit(self):
        self.server.shutdown()
        super().quit()


if __name__ == '__main__':
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # Qt从5.6.0开始，支持High-DPI
    app = QApplication(sys.argv)  #
    main = MyMainWindow()
    main.setFixedSize(main.width(), main.height())
    main.show()
    sys.exit(app.exec_())
