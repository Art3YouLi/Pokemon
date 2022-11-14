#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/14 11:47
import os
import re
import subprocess
import time
import uiautomator2 as u2
from pywinauto import Application


pic_file = ''


def subprocess_popen(statement):
    p = subprocess.Popen(statement, shell=True, stdout=subprocess.PIPE)  # 执行shell语句并定义输出格式
    while p.poll() is None:  # 判断进程是否结束（Popen.poll()用于检查子进程（命令）是否已经执行结束，没结束返回None，结束后返回状态码）
        if p.wait() != 0:  # 判断是否执行成功（Popen.wait()等待子进程结束，并返回状态码；如果设置并且在timeout指定的秒数之后进程还没有结束，将会抛出一个TimeoutExpired异常。）
            print("命令执行失败，请检查")
            print()
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
    def validate_number(self, x) -> bool:
        """Validates that the input is a number"""
        if x.isdigit():
            return True
        elif x == "":
            return True
        else:
            return False

    def validate_alpha(self, x) -> bool:
        """Validates that the input is alpha"""
        if x.isdigit():
            return False
        elif x == "":
            return True
        else:
            return True

    def validate_file(self, x) -> bool:
        """Validates that the file is existing"""
        if os.path.exists(x):
            return True
        else:
            return False

    def validate_ip(self, x) -> bool:
        """Validates that the file is existing"""
        if re.match(r'(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{'
                    r'2}|2[0-4]\d|25[0-5])\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5]):(6[0-5]{2}[0-3][0-5]|[1-5]\d{4}|['
                    r'1-9]\d{1,3}|[0-9])', x):
            return True
        else:
            return False


class ControlApp:
    def __init__(self, control_app_path, control_num, control_duration, control_times):
        self.control_app_path = control_app_path
        self.control_num = control_num
        self.control_duration = int(control_duration)
        self.control_times = int(control_times)
        self.control_app = None
        self.control_app_window = None
        global pic_file
        pic_file = os.path.join(self.control_app_path, 'ScreenShots')
        # 判断文件是否在同一文件夹
        if not os.path.exists(pic_file):
            os.mkdir(pic_file)

    def start_controlApp(self):
        self.control_app = Application(backend="uia").start(self.control_app_path)
        self.control_app_window = self.control_app.window(title='继电器控制软件')

    def exit_controlApp(self):
        self.control_app['继电器控制软件'].close()
        self.control_app['继电器控制软件']['确定'].click()

    def open_com(self):
        """打开串口"""
        self.control_app['继电器控制软件']['打开串口'].click()

    def close_com(self):
        """关闭串口"""
        self.control_app['继电器控制软件']['关闭串口'].click()

    def close_relay(self):
        """闭合继电器"""
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayClose' + self.control_num).click()

    def open_relay(self):
        """断开继电器6"""
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayOpen' + self.control_num).click()


class ScreenShotWinApp:
    """windows 桌面 app"""
    def __init__(self, win_app_path, win_app_name, win_steps):
        global pic_file
        self.win_app_path = win_app_path
        self.win_app_name = win_app_name
        self.win_steps = win_steps
        self.win_app = None
        self.win_app_pics = os.path.join(pic_file, time.strftime("%Y%m%d%H%M%S", time.localtime()))

    def create_cur_pic(self):
        if not os.path.exists(self.win_app_pics):
            os.mkdir(self.win_app_pics)

    def app_start(self):
        self.win_app = Application(backend="uia").start(self.win_app_path)

    def app_stop(self):
        self.win_app[self.win_app_name].close()

    def screen_shot(self, operate_type, times, sleep_time):
        pass
        time.sleep(sleep_time)
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.pic_file, pic_name)
        self.win_app[self.win_app_name].set_focus().capture_as_image().save(pic_path)


class ScreenShotAndroidApp:
    """Android app"""
    def __init__(self, android_ip, android_port,  android_app_name, android_steps):
        self.android_connect_info = android_ip+':'+android_port
        self.android_app_name = android_app_name
        self.device = None
        self.android_steps = android_steps
        self.and_app_pics = os.path.join(pic_file, time.strftime("%Y%m%d%H%M%S", time.localtime()))

    def create_cur_pic(self):
        if not os.path.exists(self.and_app_pics):
            os.mkdir(self.and_app_pics)

    def app_start(self):
        self.device = u2.connect(self.android_connect_info)
        time.sleep(5)
        self.device.app_stop(self.android_app_name)
        time.sleep(1)
        self.device.app_start(self.android_app_name, wait=True)

    def app_stop(self):
        self.device.app_stop(self.android_app_name)

    def screen_shot(self, operate_type, times, sleep_time=2):
        if self.android_app_btn is not None and '闭合' in operate_type:
            self.device(text=self.android_app_btn).click()
            time.sleep(1)
        time.sleep(sleep_time)
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.pic_file, pic_name)
        self.device.screenshot(pic_path)


class AutoControl:
    def __init__(self, control_app_path, control_num, control_duration, control_times, **kwargs):
        self.ca = ControlApp(control_app_path, control_num, control_duration, control_times)
        self.shot_app = None
        if kwargs.get('shot_type') == 'windows':
            win_app_path = kwargs.get('win_app_path')
            win_app_name = kwargs.get('win_app_name')
            win_steps = kwargs.get('win_steps')
            self.shot_app = ScreenShotWinApp(win_app_path, win_app_name, win_steps)
        elif kwargs.get('shot_type') == 'android':
            android_ip = kwargs.get('android_ip')
            android_port = kwargs.get('android_port')
            android_app_name = kwargs.get('android_app_name')
            android_steps = kwargs.get('android_steps')
            self.shot_app = ScreenShotAndroidApp(android_ip, android_port,  android_app_name, android_steps)

    def main_func(self):
        # 第一步：启动继电器控制软件
        self.ca.start_controlApp()
        time.sleep(3)
        # 第二步：打开串口，并断开继电器
        self.ca.open_com()
        time.sleep(3)
        self.ca.open_relay()
        # 第三步：判断是否配合其他app使用
        if self.shot_app is not None:
            self.shot_app.app_start()
            time.sleep(3)
            self.shot_app.create_cur_pic()
        # 第四步：开始循环
        for i in range(self.ca.control_times):
            # 闭合继电器
            print(f'第{str(i + 1)}次闭合继电器{self.ca.control_num}..........')
            self.ca.close_relay()

            # 出图并截图
            if self.shot_app is not None:
                pass






