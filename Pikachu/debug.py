# !/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import serial.tools.list_ports

if __name__ == '__main__':
    # 读取串口列表
    # ports_list = list(serial.tools.list_ports.comports())
    # print(ports_list)
    # if len(ports_list) <= 0:
    #     print("无串口设备")
    # else:
    #     print("可用的串口设备如下: ")
    #     print("%-5s %-10s %-65s" % ("num", "number", "name"))
    #     for i in range(len(ports_list)):
    #         comport = list(ports_list[i])
    #         comport_number, comport_name = comport[0], comport[1]
    #         print("%-5s %-10s %-65s" % (i, comport_number, comport_name))
    #         # if 'Prolific PL2303GT USB Serial COM Port' in comport_name:
    #         #     print(comport_number)
    #
    #     # 打开串口
    #     port_num = ports_list[1][0]
    #     print("默认选择串口: %s" % port_num)
    #     # 串口号: port_num, 波特率: 115200, 数据位: 7, 停止位: 2, 超时时间: 0.5秒
    #     ser = serial.Serial(port=port_num, baudrate=115200, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE,
    #                         timeout=0.5)
    #     if ser.isOpen():
    #         print("打开串口成功, 串口号: %s" % ser.name)
    #     else:
    #         print("打开串口失败")
    #
    #     # 串口发送数据
    #     data = bytearray([0xFE, 0x01, 0x06, 0x00, 0xEF])
    #     write_len = ser.write(data)
    #     print("串口发出{}个字节".format(write_len))
    #
    #     # 等待串口返回信息并输出
    #     t0 = time.time()
    #     while True:
    #         com_input = ser.read(10)
    #         t1 = time.time()
    #         t = t1 - t0
    #         print("\r等待串口接收数据, %.2f 秒" % t, end="")
    #         if com_input or t >= 3:
    #             if com_input:
    #                 print("\n%s" % com_input)
    #             else:
    #                 print("\n%s" % "没有接收到任何数据")
    #             break
    #
    #     # 关闭串口
    #     ser.close()
    #     if ser.isOpen():
    #         print("串口未关闭")
    #     else:
    #         print("串口已关闭")
    print(len('=============================begin of set parameters=================='))
