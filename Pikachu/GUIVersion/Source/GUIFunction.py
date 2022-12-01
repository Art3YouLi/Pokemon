#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/14 11:47
import os
import re
import subprocess
import sys
import time
import uiautomator2 as u2
import serial.tools.list_ports

from pywinauto import Application


def subprocess_popen(statement):
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)  # 执行shell语句并定义输出格式
    while p.poll() is None:  # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
        if p.wait() != 0:  # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果设置并且在timeout指定的秒数之后进程还没有结束，将会抛出一个TimeoutExpired异常。）
            print("命令执行失败，请检查")
            return False
        else:
            pre = p.stdout.readlines()  # 获取原始执行结果
            result = []
            for i in range(len(pre)):  # 由于原始结果需要转换编码，所以循环转为utf8编码并且去除\n换行
                res = pre[i].decode('utf-8').strip('\r\n').replace('\t', ' ').strip()
                if res != '':
                    result.append(res)
            return result


class ValidateInput:
    @staticmethod
    def validate_number(x) -> bool:
        """Validates that the input is a number"""
        if x.isdigit():
            if int(x) > 0:
                return True
            else:
                return False
        elif x == "":
            return False
        else:
            return False

    @staticmethod
    def validate_alpha(x) -> bool:
        """Validates that the input is alpha"""
        if x.isdigit():
            return False
        elif x == "":
            return False
        else:
            return True

    @staticmethod
    def validate_file(x) -> bool:
        """Validates that the file is existing"""
        if x == "":
            return False
        if os.path.exists(x):
            return True
        else:
            return False

    @staticmethod
    def validate_ip(x) -> bool:
        """Validates that the file is existing"""
        pattern = re.compile(r'(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])')
        if x == "":
            return False
        if pattern.fullmatch(x):
            return True
        else:
            return False


class ControlSerial:
    # 修改为串口发送指令方式控制继电器，不再使用UI控制
    def __init__(self, log):
        self.log = log
        self.comport_number = None
        self.ser = None

    def check_comport_exists(self):
        """
        校验当前串口是否已连接至电脑并可被识别到

        :return: flag: bool
        """
        ports_list = list(serial.tools.list_ports.comports())
        flag_exists = False
        if len(ports_list) <= 0:
            flag_exists = False
        else:
            self.log.info('      Available serial port devices are as follows:')
            self.log.info('      %-5s %-10s %-65s' % ('num', 'comport', 'name'))
            for i in range(len(ports_list)):
                comport = list(ports_list[i])
                comport_number, comport_name = comport[0], comport[1]
                self.log.info('      %-5s %-10s %-65s' % (i, comport_number, comport_name))
                if 'Prolific PL2303GT USB Serial COM Port' in comport_name:
                    self.comport_number = comport_number
                    flag_exists = True

        # 返回标志
        if flag_exists:
            self.log.info(f'      find comport: Prolific PL2303GT USB Serial COM Port, '
                          f'comport num:{self.comport_number}')
        else:
            self.log.warning('unable to find comport:Prolific PL2303GT USB Serial COM Port')
        return flag_exists

    def open_comport(self):
        """
        打开端口
        :return: flag: bool
        """
        self.log.info('      ready to open comport:' + self.comport_number)
        try:
            # 串口号: port_num, 波特率: 115200, 数据位: 7, 停止位: 2, 超时时间: 0.5秒
            self.ser = serial.Serial(port=self.comport_number, baudrate=115200, bytesize=serial.EIGHTBITS,
                                     stopbits=serial.STOPBITS_ONE, timeout=0.5)
            if self.ser.isOpen():
                self.log.info('      comport opened successfully, comport number: %s' % self.ser.name)
                return True
            else:
                self.log.info('      failed to open the comport')
                return False
        except serial.serialutil.SerialException:
            self.log.error(f'failed to open the comport, the comport {self.ser.name} has been occupied')
            return False

    def send_comport_data(self, relay_num: int, relay_state: int):
        """
        发送串口指令

        :param relay_num: 继电器编号， 1-8
        :param relay_state: 继电器状态， 1：闭合； 0：断开
        :return: flag: bool
        """
        data = bytearray([0xFE, 0x01, 0x00, 0x00, 0xEF])
        num_list = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
        state_list = bytearray([0x00, 0x01])

        # 创建指令
        data[2] = num_list[relay_num - 1]
        data[3] = state_list[relay_state]

        write_len = self.ser.write(data)
        self.log.info('      comport sends {} bytes'.format(write_len))

        # 等待串口返回信息并输出
        t0 = time.time()
        while True:
            com_input = self.ser.read(10)
            t1 = time.time()
            t = t1 - t0
            if com_input or t >= 3:
                if com_input:
                    self.log.info('      data received: %s' % com_input)
                    return True
                else:
                    self.log.warning('%s' % 'No data received')
                    return False

    def close_comport(self):
        """
        关闭端口
        """
        self.log.info('      close comport:' + self.comport_number)
        # 关闭串口
        self.ser.close()
        if self.ser.isOpen():
            self.log.warning('comport is not closed')
        else:
            self.log.info('      comport is closed')


class ScreenShotApp:
    def __init__(self, app_data, log):
        self.logcat = None
        self.logcat_file = None
        self.logcat_path = None
        self.app_data = app_data
        self.log = log
        self.app = None

        if getattr(sys, 'frozen', False):
            self.pic_file = os.path.dirname(sys.executable)
        elif __file__:
            self.pic_file = os.path.dirname(os.path.abspath(__file__))

        self.pic_file = os.path.join(self.pic_file, '../ScreenShots', self.app_data['app_name'])

    def create_pic_file(self):
        """
        创建截图文件夹

        :return:
        """
        self.log.info(f'      create Windows app screenshot file: {self.pic_file}')
        if not os.path.exists(os.path.dirname(os.path.dirname(self.pic_file))):
            os.mkdir(os.path.dirname(os.path.dirname(self.pic_file)))
        if not os.path.exists(os.path.dirname(self.pic_file)):
            os.mkdir(os.path.dirname(self.pic_file))
        if not os.path.exists(self.pic_file):
            os.mkdir(self.pic_file)

    def start_app(self):
        """
        启动app

        :return: None
        """
        flag_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.pic_file = os.path.join(self.pic_file, flag_time)
        self.create_pic_file()

        self.log.info('      start app: %s', self.app_data['app_name'])
        if self.app_data['shot_type'].lower() == 'windows':
            self.app = Application(backend="uia").start(self.app_data['app_path'])

        elif self.app_data['shot_type'].lower() == 'android':
            self.app = u2.connect(self.app_data['app_path'])
            self.app.app_start(self.app_data['app_name'], wait=True)

    def stop_app(self):
        self.log.info('      stop app: %s', str(self.app_data['app_name']))
        if self.app_data['shot_type'].lower() == 'windows':
            self.app[self.app_data['app_name']].close()
        elif self.app_data['shot_type'].lower() == 'android':
            self.app.app_stop(self.app_data['app_name'])

    def shot_steps(self):
        if len(self.app_data['steps']) > 0:
            self.log.info('      start operate app')
            for step in self.app_data['steps']:
                self.log.info(f'      click {step[0]} at {step[1]}')
                if self.app_data['shot_type'].lower() == 'windows':
                    print(step[0] + step[1])
                    self.app[step[0]][step[1]].click()
                elif self.app_data['shot_type'].lower() == 'android':
                    print({step[0]: step[1]})
                    self.app(**{step[0]: step[1]}).click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        self.log.info(f'      start screenshot app: {operate_type}第{times}次.png')
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.pic_file, pic_name)
        if self.app_data['shot_type'].lower() == 'windows':
            self.app[self.app_data['app_name']].set_focus().capture_as_image().save(pic_path)
        elif self.app_data['shot_type'].lower() == 'android':
            self.app.screenshot(pic_path)


class AutoControl:
    def __init__(self, log, control_num, control_duration, control_times, app_data):
        self.shot_app = None
        self.app_data = app_data
        self.log = log

        self.control_num = int(control_num)
        self.control_duration = int(control_duration)
        self.control_times = int(control_times)

        self.log.info('============ begin of set parameters ============')
        self.log.info(f'      parameters: control num={control_num}, control duration={control_duration}, '
                      f'control times={control_times}, shot type={self.app_data["shot_type"]}')

        if self.app_data['shot_type'] == 'windows':
            self.log.info(f'      Windows app parameters: win app path={self.app_data["app_path"]}, '
                          f'win app name={self.app_data["app_name"]}, steps={self.app_data["steps"]}')
            self.shot_app = ScreenShotApp(app_data, self.log)
        elif self.app_data['shot_type'] == 'android':
            self.log.info(f'      Android app parameters: android ip:port={self.app_data["app_path"]}, '
                          f'android app name={self.app_data["app_name"]}, steps={self.app_data["steps"]}')
            self.shot_app = ScreenShotApp(app_data, self.log)

        self.ca = ControlSerial(self.log)

    def main_func(self):
        cut_flag = False
        self.log.info('============ begin of main run ============')
        self.log.info('┌'.ljust(90, '-'))
        # 第一步：校验串口并打开串口
        if self.ca.check_comport_exists():
            if self.ca.open_comport():
                time.sleep(1)

                # 第二步：闭合继电器
                if self.ca.send_comport_data(self.control_num, 1):
                    time.sleep(1)

                    # 第三步：判断是否配合其他app使用
                    if self.app_data['shot_type'] != 'nothing':
                        self.log.info('  ***** begin of start app *****')
                        self.shot_app.start_app()
                        time.sleep(3)

                    # 第四步：开始循环
                    self.log.info('    --- begin of loop ---')
                    for i in range(int(self.control_times)):
                        # 闭合继电器并等待
                        if self.ca.send_comport_data(int(self.control_num), 1):
                            self.log.info(f'      wait for relay close')
                            time.sleep(self.control_duration)
                            # 出图并截图
                            if self.app_data['shot_type'] != 'nothing':
                                self.shot_app.shot_steps()
                                self.shot_app.screen_shot('闭合继电器并截图', i+1)
                                cut_flag = True
                            time.sleep(2)

                            # 断开继电器
                            if self.ca.send_comport_data(int(self.control_num), 0):
                                self.log.info(f'      wait for relay open')
                                time.sleep(self.control_duration)
                                # 断开继电器并截图
                                if self.app_data['shot_type'] != 'nothing':
                                    self.shot_app.screen_shot('断开继电器并截图', i+1)
                    self.log.info('    --- end loop ---')

                    # 第五步：判断是否配合其他app使用
                    if self.app_data['shot_type'] != 'nothing':
                        self.log.info('  ***** begin of close app *****')
                        self.shot_app.stop_app()
                        time.sleep(3)

        # 第五步：关闭控制程序
        self.ca.close_comport()
        self.log.info('└'.ljust(90, '-'))
        self.log.info('============ end of main run ============')

        # 第六步：打开截图文件夹
        if self.app_data['shot_type'] != 'nothing' and not cut_flag:
            self.log.info('============ open pictures file ============')
            os.startfile(self.shot_app.pic_file)
