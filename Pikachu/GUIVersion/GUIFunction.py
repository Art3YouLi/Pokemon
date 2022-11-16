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
app_pics = ''


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


class ControlApp:
    def __init__(self, control_app_path, control_num, control_duration, control_times):
        self.control_app_path = control_app_path
        self.control_num = control_num
        self.control_duration = int(control_duration)
        self.control_times = int(control_times)
        self.control_app = None
        self.control_app_window = None
        global pic_file
        pic_file = os.path.join(os.path.dirname(self.control_app_path), 'ScreenShots')
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
        global app_pics
        app_pics = self.win_app_pics

    def create_cur_pic(self):
        if not os.path.exists(self.win_app_pics):
            os.mkdir(self.win_app_pics)

    def app_start(self):
        self.win_app = Application(backend="uia").start(self.win_app_path)

    def app_stop(self):
        self.win_app[self.win_app_name].close()

    def shot_steps(self):
        if len(self.win_steps) > 0:
            for step in self.win_steps:
                self.win_app[step[0]][step[1]].click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.win_app_pics, pic_name)
        self.win_app[self.win_app_name].set_focus().capture_as_image().save(pic_path)


class ScreenShotAndroidApp:
    """Android app"""
    def __init__(self, and_ip, and_port,  and_name, and_steps):
        self.android_connect_info = and_ip+':'+and_port
        self.and_name = and_name
        self.device = None
        self.and_steps = and_steps
        self.and_app_pics = os.path.join(pic_file, time.strftime("%Y%m%d%H%M%S", time.localtime()))
        global app_pics
        app_pics = self.and_app_pics

    def create_cur_pic(self):
        if not os.path.exists(self.and_app_pics):
            os.mkdir(self.and_app_pics)

    def app_start(self):
        self.device = u2.connect(self.android_connect_info)
        time.sleep(5)
        self.device.app_stop(self.and_name)
        time.sleep(1)
        self.device.app_start(self.and_name, wait=True)

    def app_stop(self):
        self.device.app_stop(self.and_name)

    def shot_steps(self):
        if len(self.and_steps) > 0:
            for step in self.and_steps:
                if step[2] == '':
                    step[2] = 0
                self.device(**{step[0]: step[1]}).click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.and_app_pics, pic_name)
        self.device.screenshot(pic_path)


class AutoControl:
    def __init__(self, control_app_path, control_num, control_duration, control_times, shot_type, **kwargs):
        self.ca = ControlApp(control_app_path, control_num, control_duration, control_times)
        self.shot_type = shot_type
        self.shot_app = None
        print(kwargs)
        if self.shot_type == 'windows':
            win_app_path = kwargs.get('win_app_path')
            win_app_name = kwargs.get('win_app_name')
            win_steps = kwargs.get('steps')
            self.shot_app = ScreenShotWinApp(win_app_path, win_app_name, win_steps)
        elif self.shot_type == 'android':
            and_ip = kwargs.get('and_ip')
            and_port = kwargs.get('and_port')
            and_name = kwargs.get('and_name')
            and_steps = kwargs.get('steps')
            self.shot_app = ScreenShotAndroidApp(and_ip, and_port,  and_name, and_steps)

    def main_func(self):
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
            self.shot_app.app_start()
            time.sleep(3)
            self.shot_app.create_cur_pic()
        # 第四步：开始循环
        for i in range(self.ca.control_times):
            # 闭合继电器并等待
            print(f'第{str(i + 1)}次闭合继电器{self.ca.control_num}..........')
            self.ca.close_relay()
            time.sleep(self.ca.control_duration)
            # 出图并截图
            if self.shot_type != 'nothing':
                self.shot_app.shot_steps()
                self.shot_app.screen_shot(f'第{i+1}次闭合继电器并截图', i+1)
            print(f'第{str(i + 1)}次闭合继电器等待..........')

            # 断开继电器
            print(f'第{str(i + 1)}次断开继电器{self.ca.control_num}..........')
            self.ca.open_relay()
            time.sleep(self.ca.control_duration)
            # 断开继电器并截图
            if self.shot_type != 'nothing':
                self.shot_app.screen_shot(f'第{i + 1}次断开继电器并截图', i+1)
            print(f'第{str(i + 1)}次断开继电器等待..........')

        # 第五步：关闭控制程序
        print(f'正在断开串口并关闭控制程序..........')
        self.ca.close_com()
        self.ca.exit_controlApp()

        # 第六步：打开截图文件夹
        if app_pics != '':
            os.startfile(app_pics)
