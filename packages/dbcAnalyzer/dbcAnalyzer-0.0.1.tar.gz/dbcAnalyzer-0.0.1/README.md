# dbcAnalyzer
dbc解析工具
##Information/说明
Hey, this is a analyzer to get what you want in a dbc file:

通过使用dbc解析工具，你可以在一个dbc文件中获取到：

·a dbc file's version

dbc文件的版本

·all nodes,messages or signals in a dbc file;

dbc文件下的所有节点名称、报文名称、信号名称

·a message's ID, Size, Transmitter or it's signals;

获取某一帧报文的ID,Size,Transmitter

·a signal's Value Table, Size, StartBit, Factor, OffSet, Min/Max value; 

获取某个信号的Value Table,Size,起始位，精度，偏移量，最小/最大值

## Installation / 安装

Get dbcAnalyzer by pip(通过pip安装dbcAnalyzer)

`pip install dbcAnalyzer`

## APIs / 程序接口调用

```
from dbcAnalyzer import dbc as db

dbc = db.DBC('your dbc file')  
version = dbc.getVersion()  # 获取dbc版本
message = dbc.getMessages()  # 获取报文
signal = dbc.getSignals()  # 获取信号
node = dbc.getNodes()  # 获取节点
messageID = dbc.getMsgID('message name')  # 获取报文ID  
messageSize = dbc.getMsgSize('message name')  # 获取报文Size
messageTransmitter = dbc.getMsgTransmitter('message name')  # 获取报文发送节点  
messageSignal = dbc.getMsgSignal('message name')  # 获取报文包含的信号
signalValue = dbc.getSigVal('signal name')  # 获取信号Value Table
signalSize = dbc.getSigSize('signal name')  # 获取信号Size
signalStartBit = dbc.getSigStrtBit('signal name')  # 获取信号起始位
signalFactor = dbc.getSigFac('signal name')  # 获取信号精度
signalOffSet = dbc.getSigOff('signal name')  # 获取信号偏移量
signalMin = dbc.getSigMin('signal name')  # 获取信号最小值
signalMax = dbc.getSigMax('signal name')  # 获取信号最大值

print(version,message,'...',signalMax)
```






