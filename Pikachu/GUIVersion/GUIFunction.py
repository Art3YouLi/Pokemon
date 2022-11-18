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
            self.log.info('-------------------Available serial port devices are as follows:-------------------')
            print('%-5s %-10s %-65s' % ('num', 'comport', 'name'))
            for i in range(len(ports_list)):
                comport = list(ports_list[i])
                comport_number, comport_name = comport[0], comport[1]
                print("%-5s %-10s %-65s" % (i, comport_number, comport_name))
                if 'Prolific PL2303GT USB Serial COM Port' in comport_name:
                    self.comport_number = comport_number
                    flag_exists = True

        # 返回标志
        if flag_exists:
            self.log.info(f'find comport:Prolific PL2303GT USB Serial COM Port, comport num:{self.comport_number}')
        else:
            self.log.warning('unable to find comport:Prolific PL2303GT USB Serial COM Port')
        return flag_exists

    def open_comport(self):
        """
        打开端口
        :return: flag: bool
        """
        self.log.info('ready to open comport:'+self.comport_number)
        try:
            # 串口号: port_num, 波特率: 115200, 数据位: 7, 停止位: 2, 超时时间: 0.5秒
            self.ser = serial.Serial(port=self.comport_number, baudrate=115200, bytesize=serial.EIGHTBITS,
                                     stopbits=serial.STOPBITS_ONE, timeout=0.5)
            if self.ser.isOpen():
                self.log.info('comport opened successfully, comport number: %s' % self.ser.name)
                return True
            else:
                self.log.info('failed to open the comport')
                return False
        except serial.serialutil.SerialException:
            self.log.info(f'failed to open the comport, the comport {self. ser. name} has been occupied')
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
        data[2] = num_list[relay_num-1]
        data[3] = state_list[relay_state]

        write_len = self.ser.write(data)
        self.log.info('comport sends {} bytes'.format(write_len))

        # 等待串口返回信息并输出
        t0 = time.time()
        while True:
            com_input = self.ser.read(10)
            t1 = time.time()
            t = t1 - t0
            if com_input or t >= 3:
                if com_input:
                    self.log.info('data received: \n%s' % com_input)
                    return True
                else:
                    self.log.warning('\n%s' % 'No data received')
                    return False

    def close_comport(self):
        """
        关闭端口
        :return: flag: bool
        """
        self.log.info('close comport:'+self.comport_number)
        # 关闭串口
        self.ser.close()
        if self.ser.isOpen():
            self.log.warning('comport is not closed')
        else:
            self.log.info('comport is closed')


class ScreenShotApp:
    def __init__(self, app_info, steps, log):
        self.logcat = None
        self.logcat_file = None
        self.logcat_path = None
        self.app_info = app_info
        self.steps = steps
        self.log = log
        self.app = None

        if getattr(sys, 'frozen', False):
            self.pic_file = os.path.dirname(sys.executable)
        elif __file__:
            self.pic_file = os.path.dirname(os.path.abspath(__file__))
        self.pic_file = os.path.join(self.pic_file, 'ScreenShots', self.app_info['app_name'])

    def create_pic_file(self):
        """
        创建截图文件夹

        :return:
        """
        self.log.info(f'create Windows app screenshot file: {self.pic_file}')
        if not os.path.exists(self.pic_file):
            os.mkdir(self.pic_file)

    def app_start(self):
        """
        启动app

        :return: None
        """
        flag_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self.pic_file = os.path.join(self.pic_file, flag_time)
        self.create_pic_file()

        if self.app_info['type'].lower() == 'windows':
            self.log.info('start app: %s', self.app_info['app_name'])
            self.app = Application(backend="uia").start(self.app_info['app_path'])

        elif self.app_info['type'].lower() == 'android':
            self.log.info('start app: %s', self.app_info['app_name'])
            self.app = u2.connect(self.app_info['app_path'])
            self.app.service('uiautomator').stop()
            # Maxim正常运行
            # stream模式，保证不会timeout导致杀掉，底层上是一个requests库提供的streaming 模式的response
            task = self.app.shell(
                'CLASSPATH=/sdcard/monkey.jar:/sdcard/framework.jar exec app_process /system/bin '
                'tv.panda.test.monkey.Monkey -p com.hotbitmapgg.ohmybilibili --running-minutes 2 --throttle 1500 '
                '--uiautomatormix --output-directory /sdcard/max-output',
                stream=True)
            try:
                for line in task.iter_lines():
                    self.log.info(line)
            finally:
                task.close()
            # 重新让atx-agent拉活uiautomator-server进程，或者执行下一条需要uiautomator-server的命令也会自行拉活
            self.app.service('uiautomator').start()
            self.app.set_fastinput_ime(True)  # 启用自动化定制的输入法，防止各机型输入法不同导致出错
            self.app.settings['operation_delay_methods'] = ['click', 'swipe', 'drag', 'press']
            # 设置隐式等待时间，默认20s
            self.app.implicitly_wait(20)
            with self.app.watch_context(builtin=True) as ctx:
                # 注意：这里不再对app内系统权限提示窗做监视
                ctx.when("^(下载|更新)").when("取消").click()  # 当同时出现（下载 或 更新）和 取消 按钮时，点击取消
                ctx.when("跳过%").click()
                ctx.when("继续").click()
                ctx.when("每次开启").click()
                ctx.when("创建").when("取消").click()
                ctx.when("恢复").when("取消").click()
                ctx.wait_stable(seconds=0.5)  # 开启弹窗监控，并等待界面稳定（两个弹窗检查周期内没有弹窗代表稳定）

            self.logcat_path = os.path.join(self.pic_file, 'logcat')
            if not os.path.exists(self.logcat_path):  # 判断地址是否存在，否则就新建
                os.makedirs(self.logcat_path)
            logcat_filename = os.path.join(self.logcat_path, flag_time + '.txt')
            self.logcat_file = open(logcat_filename, 'w')
            os.system(f"adb -s {self.app_info['app_path'] } logcat -c")  # 清除所有日志缓存信息
            self.logcat = subprocess.Popen(f"adb -s {self.app_info['app_path']} logcat -v time",
                                           stdout=self.logcat_file, stderr=subprocess.PIPE)  # 开子进程将日志输出到指定文件
            self.log.info('start capturing log: %s', str(self.logcat_file))
            self.log.info('start app: %s', str(self.app_info['app_name']))
            self.app.app_start(self.app_info['app_name'], wait=True)

    def app_stop(self):
        if self.app_info['type'].lower() == 'windows':
            self.log.info('stop app: %s', str(self.app_info['app_name']))
            self.app[self.app_info['app_name']].close()

        elif self.app_info['type'].lower() == 'android':
            self.logcat_file.close()
            self.logcat.terminate()  # 停止日志捕获
            self.log.info('stop capturing log')
            self.log.info('stop app: %s', str(self.app_info['app_name']))
            self.app.app_stop(self.app_info['app_name'])

    def shot_steps(self):
        if len(self.steps) > 0:
            self.log.info('start operate app')
            for step in self.steps:
                self.log.info(f'click {step[0]} at {step[1]}')
                if self.app_info['type'].lower() == 'windows':
                    self.app[step[0]][step[1]].click()
                elif self.app_info['type'].lower() == 'android':
                    self.app(**{step[0]: step[1]}).click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        self.log.info(f'start screenshot app: {operate_type}第{times}次.png')
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.pic_file, pic_name)
        if self.app_info['type'].lower() == 'windows':
            self.app[self.app_info['app_name']].set_focus().capture_as_image().save(pic_path)
        elif self.app_info['type'].lower() == 'android':
            self.app.screenshot(pic_path)


class AutoControl:
    def __init__(self, control_app_path, control_num, control_duration, control_times, shot_type, log, **kwargs):
        self.log = log
        self.log.info('--------- begin of set parameters')
        self.ca = ControlApp(control_app_path, control_num, control_duration, control_times, self.log)
        self.shot_type = shot_type
        self.shot_app = None
        self.log.info(f'parameters: control app path={control_app_path}, control num={control_num}, '
                      f'control duration={control_duration}, control_times={control_times}, shot_type={shot_type}')
        if self.shot_type == 'windows':
            win_app_path = kwargs.get('win_app_path')
            win_app_name = kwargs.get('win_app_name')
            win_steps = kwargs.get('steps')
            self.log.info(f'Windows app parameters: win app path={win_app_path}, win_app_name={win_app_name}, '
                          f'steps={win_steps}')
            self.shot_app = ScreenShotWinApp(win_app_path, win_app_name, win_steps, self.log)
        elif self.shot_type == 'android':
            and_ip = kwargs.get('and_ip')
            and_port = kwargs.get('and_port')
            and_name = kwargs.get('and_name')
            and_steps = kwargs.get('steps')
            self.log.info(f'Android app parameters: android ip={and_ip}, android port={and_port}, '
                          f'android app name={and_name}, steps={and_steps}')
            self.shot_app = ScreenShotAndroidApp(and_ip, and_port, and_name, and_steps, self.log)

    def main_func(self):
        self.log.info('--------- begin of main run')
        # 第一步：启动继电器控制软件
        self.ca.start_controlApp()
        time.sleep(3)

        # 第二步：打开串口，并断开继电器
        self.ca.open_com()
        time.sleep(2)
        self.ca.open_relay()
        time.sleep(2)

        # 第三步：判断是否配合其他app使用
        if self.shot_type != 'nothing':
            self.log.info('--------- begin of starting app')
            self.shot_app.app_start()
            time.sleep(3)
            self.shot_app.create_cur_pic()
        # 第四步：开始循环
        self.log.info('--------- begin of loop')
        for i in range(self.ca.control_times):
            # 闭合继电器并等待
            self.ca.close_relay()
            self.log.info(f'wait for relay close')
            time.sleep(self.ca.control_duration)
            # 出图并截图
            if self.shot_type != 'nothing':
                self.shot_app.shot_steps()
                self.shot_app.screen_shot(f'第{i + 1}次闭合继电器并截图', i + 1)
            time.sleep(2)

            # 断开继电器
            self.ca.open_relay()
            self.log.info(f'wait for relay open')
            time.sleep(self.ca.control_duration)
            # 断开继电器并截图
            if self.shot_type != 'nothing':
                self.shot_app.screen_shot(f'第{i + 1}次断开继电器并截图', i + 1)
        self.log.info('--------- end loop')

        # 第五步：关闭控制程序
        self.ca.close_com()
        self.ca.exit_controlApp()
        self.log.info('--------- end of main run')

        # 第六步：打开截图文件夹
        if app_pics != '':
            self.log.info('--------- open pictures file')
            os.startfile(app_pics)
