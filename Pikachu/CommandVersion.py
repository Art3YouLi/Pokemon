#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/10/26 10:59

import os
import subprocess
import time
import sys
import uiautomator2 as u2

from pywinauto.application import Application


class ControlApp:
    def __init__(self):
        self.control_app = None
        self.control_app_file_path = None
        self.control_app_path = None
        self.control_app_name = '继电器控制软件8路.exe'
        self.control_app_window = None
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            self.control_app_file_path = os.path.dirname(sys.executable)
        elif __file__:
            self.control_app_file_path = os.path.dirname(os.path.abspath(__file__))
        self.control_app_path = os.path.join(self.control_app_file_path, self.control_app_name)

    def check_controlApp(self):
        # 判断文件是否在同一文件夹
        if os.path.exists(self.control_app_path):
            return True
        else:
            print('继电器控制软件8路.exe与当前exe文件不在同一路径下，请检查')
            return False

    def start_controlApp(self):
        self.control_app = Application(backend="uia").start(self.control_app_path)
        self.control_app_window = self.control_app.window(title='继电器控制软件')
        # 打印当前窗口的所有controller（控件和属性） 调试用
        # self.main_app_window.print_control_identifiers(depth=None, filename=None)

    def exit_controlApp(self):
        self.control_app['继电器控制软件'].close()
        self.control_app['继电器控制软件']['确定'].click()

    def open_com(self):
        """打开串口"""
        self.control_app['继电器控制软件']['打开串口'].click()

    def close_com(self):
        """打开串口"""
        self.control_app['继电器控制软件']['关闭串口'].click()

    def close_relay(self, number: str):
        """闭合继电器"""
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayClose' + number).click()

    def open_relay(self, number: str):
        """断开继电器6"""
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayOpen' + number).click()


class ScreenShotWinApp:
    """windows 桌面 app"""

    def __init__(self, win_app_path, win_app_name, pic_file):
        self.win_app_path = win_app_path
        self.win_app_name = win_app_name
        self.pic_file = pic_file
        self.win_app = None

    def check_exits(self):
        if os.path.exists(self.win_app_path):
            return True
        else:
            return False

    def app_start(self):
        self.win_app = Application(backend="uia").start(self.win_app_path)

    def app_stop(self):
        self.win_app[self.win_app_name].close()

    def screen_shot(self, operate_type, times, sleep_time):
        if '闭合' in operate_type:
            if self.win_app_name == 'FalconApplication':
                self.win_app[self.win_app_name]['刷新'].click()
                time.sleep(1)
                self.win_app[self.win_app_name]['连接'].click()
                time.sleep(1)
            elif self.win_app_name == 'Falcon-DeveloperTool':
                self.win_app[self.win_app_name]['刷新'].click()
                time.sleep(1)
                self.win_app[self.win_app_name]['连接'].click()
                time.sleep(1)
                self.win_app[self.win_app_name]['出图'].click()
                time.sleep(1)
        time.sleep(sleep_time)
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.pic_file, pic_name)
        self.win_app[self.win_app_name].set_focus().capture_as_image().save(pic_path)


class ScreenShotAndroidApp:
    """Android app"""

    def __init__(self, android_connect_info, android_app_name, pic_file, android_app_btn):
        self.android_connect_info = android_connect_info
        self.android_app_name = android_app_name
        self.pic_file = pic_file
        self.device = None
        self.android_app_btn = android_app_btn

    def check_exits(self):
        res = subprocess_popen('adb devices')
        if self.android_connect_info + ' device' in res:
            return True
        else:
            return False

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


def title_info():
    """提示信息"""
    print('=====================================================')
    print('欢迎使用Auto Control BMW8015！！！')
    print('当前版本号：v1.0.1')
    print('正式开始使用前请注意：')
    print('    1. 请确保继电器已成功连接至电脑并正确安装驱动！！！')
    print('    2. 请确保继电器控制软件8路.exe与当前exe文件在同一路径下！！！')
    print('    3. 默认第一次断开继电器！！！')
    print('    4. 使用方式：')
    print('        a. 满足上述条件后双击运行')
    print('        b. 输入需要控制的继电器序号后回车')
    print('        c. 输入闭合断开继电器时间间隔后回车')
    print('        d. 输入需要重复闭合断开次数后回车（闭合断开为1次）')
    print('        e. 选择需要截图设备类型')
    print('        f. 输入需要被截图app信息')
    print('        g. 等待运行')
    print('    5. 每次输入仅有3次机会！！！')
    print('    6. app信息（Windows app窗口名称、Android app包名）无法校验，请自行检查！！！')
    print('    7. 详细使用说明请查看附带README.md文档！！！')
    print('若需要源码或有任何问题，请联系我zewen.fang@infisense.cn')
    print('=====================================================')


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


def create_picFile(pic_file):
    # 判断文件是否在同一文件夹
    if not os.path.exists(pic_file):
        os.mkdir(pic_file)
    return pic_file


def main_func():
    num = None
    sleep_time = None
    open_times = None

    # 提示信息
    title_info()

    # 确认是否开始使用
    enter_flag = input('若已确认，开始使用，请输入Y/y并回车进入，否则请输入N/n并回车退出：')
    if enter_flag.lower() == 'y':
        ca = ControlApp()
        screenshot_app = None
        exit_flag = False
        pic_file = None
        sys_type = None
        android_app_btn = None

        # 判断文件是否在同一文件夹
        if not ca.check_controlApp():
            exit_flag = True

        # 输入继电器序号
        input_count = 0
        while not exit_flag:
            num = input('请输入要控制的继电器序号1~8并回车：')
            if not num.isdigit() or int(num) < 1 or int(num) > 8:
                print('输入的序号不符合条件，请检查')
                input_count += 1
            else:
                break
            if input_count > 2:
                exit_flag = True
            else:
                exit_flag = False

        # 输入继电器闭合断开隔时间
        input_count = 0
        while not exit_flag:
            sleep_time = input('请输入闭合断开继电器时间间隔并回车(最少1s)：')
            if not sleep_time.isdigit() or int(sleep_time) < 1:
                print('输入的时间间隔不符合条件，请检查')
                input_count += 1
            else:
                break
            if input_count > 2:
                exit_flag = True
            else:
                exit_flag = False

        # 输入继电器闭合断开次数
        input_count = 0
        while not exit_flag:
            open_times = input('请输入闭合断开继电器的次数(最少1次)：')
            if not open_times.isdigit() or int(open_times) < 1:
                print('输入的闭合断开次数不符合条件，请检查')
                input_count += 1
            else:
                break
            if input_count > 2:
                exit_flag = True
            else:
                exit_flag = False
                input_count = 0

        # 输入截图设备类型
        input_count = 0
        while not exit_flag:
            sys_type = input('请选择需要截图设备类型（1.Windows；2.Android）：')
            if not sys_type.isdigit() or sys_type not in ['1', '2']:
                print('选择需要截图设备类型不存在，请检查')
                input_count += 1
            else:
                pic_file_name = 'ScreenShot' + time.strftime("%Y%m%d%H%M%S", time.localtime())
                pic_file = os.path.join(ca.control_app_file_path, pic_file_name)
                # win app
                if sys_type == '1':
                    win_app_path = input('请输入需要被截图app完整路径并回车：')
                    win_app_name = input('请输入需要被截图窗口名称并回车：')
                    screenshot_app = ScreenShotWinApp(win_app_path, win_app_name, pic_file)
                    if not screenshot_app.check_exits():
                        print('需要被截图app路径错误，请检查')
                        input_count += 1
                    else:
                        screenshot_app.app_start()
                        break
                # Android app
                else:
                    android_connect_info = input('请输入需要被截图设备信息并回车（信息格式ip:port ）：')
                    android_app_name = input('请输入需要被截图app包名：')
                    if 'com.infisense.usb' in android_app_name:
                        android_app_type = input('请确认app出图前是否有前置操作并回车（如SDK测试的demo app需要点击出图按钮）（y/n）：')
                        if android_app_type.lower() == 'y':
                            android_app_btn = input('请输入出图操作按钮名称并回车：')
                    screenshot_app = ScreenShotAndroidApp(android_connect_info, android_app_name,
                                                          pic_file, android_app_btn)
                    if not screenshot_app.check_exits():
                        print('需要被截图设备信息错误，请检查')
                        input_count += 1
                    else:
                        screenshot_app.app_start()
                        break
            if input_count > 2:
                exit_flag = True
            else:
                exit_flag = False

        if not exit_flag:
            print('当前设置参数为：')
            print(f'    控制的继电器序号：{num}')
            print(f'    闭合断开时间间隔：{sleep_time}s')
            print(f'    闭合断开次数：{open_times}次')
            if sys_type == '1':
                print(f'    截图应用为：{screenshot_app.win_app_name}')
            else:
                print(f'    截图应用为：{screenshot_app.android_app_name}')
            print('=====================================================')
            print()
            print('即将开始程序..........')
            print('正在创建截图文件夹..........')
            create_picFile(pic_file)
            print('正在打开控制程序..........')
            ca.start_controlApp()
            print('正在打开串口..........')
            ca.open_com()
            print(f'开始执行{open_times}次闭合断开继电器{num}操作..........')
            for i in range(int(open_times)):
                # 断开继电器并
                print(f'第{str(i + 1)}次断开继电器{num}..........')
                ca.open_relay(num)
                screenshot_app.screen_shot('断开继电器', str(i + 1), 2)

                print(f'第{str(i + 1)}次闭合继电器{num}..........')
                ca.close_relay(num)
                screenshot_app.screen_shot('闭合继电器', str(i + 1), int(sleep_time))
            print(f'正在断开串口并关闭控制程序..........')
            ca.close_com()
            ca.exit_controlApp()

    os.system('pause')


if __name__ == '__main__':
    main_func()
