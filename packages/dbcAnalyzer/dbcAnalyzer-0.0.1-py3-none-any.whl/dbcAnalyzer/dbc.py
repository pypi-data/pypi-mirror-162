# -*- coding: utf-8 -*-
# @Time : 2022/8/4 18:00
# @Author : 人民当有信仰
# @CSDN: 李白LeeBai
# @File : dbcAnalyzer.py
# @Project : dbcAnalyzer

import re
import sqlite3
import threading
from sqlite3 import Error


class DBC:
    def __init__(self, dbc):
        self.__dbc = dbc  # dbc
        # 数据库连接
        self.__con = sqlite3.connect(f'{self.__dbc}.db')
        # 创建游标
        self.__cur = self.__con.cursor()
        # 检查dbc版本变更
        self.__checkRet = self.__CheckVersion()
        # 初始化报文名列表
        self.__msgNameLst = []
        # 初始化报文ID列表
        self.__msgIDLst = []
        # 初始化报文Size列表
        self.__msgSizeLst = []
        # 初始化报文TR列表
        self.__msgTrLst = []
        # 初始化节点列表
        self.__nodeLst = []
        # 初始化信号列表
        self.__sigLst = []
        # 初始化信号起始位列表
        self.__sigStrtBitLst = []
        # 初始化信号长度列表
        self.__sigSizeLst = []
        # 初始化信号精度列表
        self.__sigFactorLst = []
        # 初始化信号偏移量列表
        self.__sigOffSetLst = []
        # 初始化信号最小值列表
        self.__sigMinLst = []
        # 初始化信号最大值列表
        self.__sigMaxLst = []
        # 创建数据库
        try:
            self.__CreateTb()
        except Error:
            pass
        if not self.__checkRet:  # 若版本不一致
            self.__UpdateDBC()
            t1 = threading.Thread(target=self.__insertNodes)
            t1.start()
            t2 = threading.Thread(target=self.__insertMsgs)
            t2.start()
            t3 = threading.Thread(target=self.__insertSigs)
            t3.start()
        else:
            print('No dbc version change')

    def __UpdateDBC(self):
        '''
        DBC更新
        :return:
        '''
        with open(self.__dbc, 'r', encoding='ANSI') as f:
            __lines = f.readlines()
        for item in __lines:
            BU_ = re.findall(r'^BU_.*$', item)  # 节点
            BO_ = re.findall(r'^BO_.*$', item)  # 报文
            SG_ = re.findall(r'^ SG_.*', item)  # 信号
            if BU_:
                self.__nodeLst = re.findall(r'\w*\w', BU_[0])
                del self.__nodeLst[0]
            if BO_:
                msg = re.findall(r'\w*\w', BO_[0])
                self.__msgNameLst.append(msg[2])
                self.__msgIDLst.append(msg[1])
                self.__msgSizeLst.append(msg[3])
                self.__msgTrLst.append(msg[4])
            if SG_:
                sig = re.findall(r'0\.\d+|\w*\w', SG_[0])
                self.__sigLst.append(sig[1])
                self.__sigStrtBitLst.append(sig[2])
                self.__sigSizeLst.append(sig[3])
                self.__sigFactorLst.append(sig[5])
                self.__sigOffSetLst.append(sig[6])
                self.__sigMinLst.append(sig[7])
                self.__sigMaxLst.append(sig[8])

    def __CreateTb(self):
        '''
        创建数据表
        :return:
        '''
        Sql_Create_Nodes = "create table Nodes (ID integer primary key autoincrement, NodeName varchar(50) " \
                           "UNIQUE ON CONFLICT IGNORE)"
        Sql_Create_Msgs = "create table Messages (ID integer primary key autoincrement,MessageID integer," \
                          "MessageName varchar(50) UNIQUE ON CONFLICT IGNORE, MessageSize integer, " \
                          "MessageTransmitter varchar(50))"
        Sql_Create_Sigs = "create table Signals (ID integer primary key autoincrement, " \
                          "SignalName varchar(50) UNIQUE ON CONFLICT IGNORE," \
                          "StartBit integer,SignalSize integer,Factor double,Offset double,Min double," \
                          "Max double,Receiver varchar(50))"
        self.__cur.execute(Sql_Create_Nodes)
        self.__cur.execute(Sql_Create_Msgs)
        self.__cur.execute(Sql_Create_Sigs)
        self.__con.close()

    def __insertNodes(self):
        '''
        数据库写入节点
        :return:
        '''
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        # 获取节点，写入数据库
        for node in self.__nodeLst:
            cursor.execute("INSERT INTO Nodes (ID, NodeName) VALUES (NULL,?)", (node,))
        con.commit()
        con.close()

    def __insertMsgs(self):
        '''
        数据库写入报文
        :return:
        '''
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        # 获取报文，写入数据库
        for i in range(len(self.__msgNameLst)):
            cursor.execute("INSERT INTO Messages (ID, MessageID, MessageName,  MessageSize,MessageTransmitter) "
                           "VALUES (NULL,?,?,?,?)", (self.__msgIDLst[i], self.__msgNameLst[i],
                                                     self.__msgSizeLst[i], self.__msgTrLst[i],))
        con.commit()
        con.close()

    def __insertSigs(self):
        '''
        数据库写入信号
        :return:
        '''
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        # 获取信号，写入数据库
        for i in range(len(self.__sigLst)):
            cursor.execute(
                "INSERT INTO Signals (ID, SignalName, StartBit, SignalSize, Factor, Offset, Min, Max) "
                "VALUES (NULL,?,?,?,?,?,?,?)", (self.__sigLst[i], self.__sigStrtBitLst[i],
                                                self.__sigSizeLst[i], self.__sigFactorLst[i],
                                                self.__sigOffSetLst[i], self.__sigMinLst[i],
                                                self.__sigMaxLst[i],))
        con.commit()
        con.close()

    def __CheckVersion(self):
        '''
        初始化时查验dbc版本
        :return: old_version
        '''
        __new_version = self.GetVersion()
        try:
            with open('version.ini', 'r', encoding='utf-8') as f:
                __old_version = f.readline()
        except:
            with open('version.ini', 'w', encoding='utf-8') as f:
                f.write(__new_version)
            __old_version = __new_version
            return False
        if self.__dbc + __old_version == self.__dbc + __new_version:
            return True
        else:
            with open('version.ini', 'w', encoding='utf-8') as f:
                f.write(__new_version)
            return False

    def GetVersion(self):
        '''
        获取dbc版本
        :return: dbc.version
        '''
        with open(self.__dbc, 'r', encoding='ANSI') as f:
            version = f.readline()
            while 'VERSION' not in version:
                version = f.readline()
            return version

    def getNodes(self):
        '''
        获取节点列表
        :param dbc: dbc files
        :return: [Nodes]
        '''
        nodes = []
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT NodeName FROM Nodes')
        fetch = cursor.fetchall()
        con.close()
        for item in fetch:
            node = item[0].replace(',', '')
            nodes.append(node)
        return nodes

    def getMessage(self):
        '''
        获取报文列表
        :param dbc: dbc files
        :return: [dbc.Message]
        :message = BO_ message_id message_name ':' message_size transmitter {signal} ;
        '''
        messages = []
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT MessageName FROM Messages')
        fetch = cursor.fetchall()
        con.close()
        for item in fetch:
            message = item[0].replace(',', '')
            messages.append(message)
        return messages

    def getSignal(self):
        '''
        获取信号列表
        :param dbc:dbc files
        :return:[dbc.signals]
        signal = 'SG_' signal_name multiplexer_indicator ':' start_bit '|'
        signal_size '@' byte_order value_type '(' factor ',' offset ')'
        '[' minimum '|' maximum ']' unit receiver {',' receiver} ;
        '''
        signals = []
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT SignalName FROM Signals')
        fetch = cursor.fetchall()
        con.close()
        for item in fetch:
            signal = item[0].replace(',', '')
            signals.append(signal)
        return signals

    def getMsgID(self, msgname):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT MessageID FROM Messages WHERE MessageName = (?)', (msgname,))
        msgID = cursor.fetchone()[0]
        con.close()
        return msgID

    def getMsgSize(self, msgname):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT MessageSize FROM Messages WHERE MessageName = (?)', (msgname,))
        msgSize = cursor.fetchone()[0]
        con.close()
        return msgSize

    def getMsgTrasmitter(self, msgname):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT MessageTransmitter FROM Messages WHERE MessageName = (?)', (msgname,))
        tr = cursor.fetchone()[0]
        con.close()
        return tr

    def getMsgSignal(self, msgname):
        __msgSig = {}
        sigLst = []
        with open(self.__dbc, 'r', encoding='ANSI') as f:
            __res = f.readlines()
        for item in __res:
            if item[0:3] == 'BO_':
                res = re.findall(r'\w*\w', item)
                msg = res[2]
                __msgSig[msg] = sigLst
            elif item[0:3] == ' SG':
                res = re.findall(r'\w*\w', item)
                sig = res[1]
                sigLst.append(sig)
            elif item == '\n':
                sigLst = []
            else:
                pass
        return __msgSig[msgname]

    def getSigVal(self, signame):
        '''
        获取信号的value table返回一个字典
        :param signame:
        :return:
        '''
        sigDict = {}  # signal 字典{signalname: valDict}
        valDict = {}  # value table字典{key: value}
        with open(self.__dbc, 'r', encoding='ANSI') as f:
            result = f.readlines()
            for item in result:
                VAL_ = re.findall(r'^VAL_.*$', item)  # value table
                if VAL_:
                    __valname = re.findall(r'\w*\w', VAL_[0])[2]  # 获取信号名
                    __valtb = re.findall(r'[\d]+ "\w.*?"', VAL_[0])  # 获取value table
                    for tb in __valtb:
                        k = tb[0:3].replace(' ', '').replace('\"', '')
                        v = re.findall(r'\".*?\"', tb)[0].replace('\"', '')
                        valDict[k] = v
                    sigDict[__valname] = valDict
                    valDict = {}
        return sigDict[signame]

    def getSigStrtBit(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT StartBit FROM Signals WHERE SignalName = (?)', (signame,))
        strtbit = cursor.fetchone()[0]
        con.close()
        return strtbit

    def getSigSize(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT SignalSize FROM Signals WHERE SignalName = (?)', (signame,))
        sigsize = cursor.fetchone()[0]
        con.close()
        return sigsize

    def getSigMin(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT Min FROM Signals WHERE SignalName = (?)', (signame,))
        min = cursor.fetchone()[0]
        con.close()
        return min

    def getSigMax(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT Max FROM Signals WHERE SignalName = (?)', (signame,))
        max = cursor.fetchone()[0]
        con.close()
        return max

    def getSigFac(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT Factor FROM Signals WHERE SignalName = (?)', (signame,))
        factor = cursor.fetchone()[0]
        con.close()
        return factor

    def getSigOff(self, signame):
        con = sqlite3.connect(f'{self.__dbc}.db')
        cursor = con.cursor()
        cursor.execute(f'SELECT Offset FROM Signals WHERE SignalName = (?)', (signame,))
        offset = cursor.fetchone()[0]
        con.close()
        return offset
