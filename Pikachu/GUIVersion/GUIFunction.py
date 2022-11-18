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
    # TODO: 修改为串口发送指令方式控制继电器，不再使用UI控制
    def __init__(self, control_app_path, control_num, control_duration, control_times, log):
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
        self.log = log

    def start_controlApp(self):
        self.log.info(f'start controlApp: {self.control_app_path}')
        self.control_app = Application(backend="uia").start(self.control_app_path)
        self.control_app_window = self.control_app.window(title='继电器控制软件')

    def exit_controlApp(self):
        self.log.info(f'exit controlApp: {self.control_app_path}')
        self.control_app['继电器控制软件'].close()
        self.control_app['继电器控制软件']['确定'].click()

    def open_com(self):
        """打开串口"""
        self.log.info(f'open com: {self.control_app_path}')
        self.control_app['继电器控制软件']['打开串口'].click()

    def close_com(self):
        """关闭串口"""
        self.log.info(f'close com: {self.control_app_path}')
        self.control_app['继电器控制软件']['关闭串口'].click()

    def close_relay(self):
        """闭合继电器"""
        self.log.info(f'close relay: {self.control_num}')
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayClose' + self.control_num).click()

    def open_relay(self):
        """断开继电器6"""
        self.log.info(f'open relay: {self.control_num}')
        self.control_app['继电器控制软件'].window(auto_id='BtnRelayOpen' + self.control_num).click()


class ScreenShotWinApp:
    """windows 桌面 app"""

    def __init__(self, win_app_path, win_app_name, win_steps, log):
        global pic_file
        self.win_app_path = win_app_path
        self.win_app_name = win_app_name
        self.win_steps = win_steps
        self.win_app = None
        self.win_app_pics = os.path.join(pic_file, time.strftime("%Y%m%d%H%M%S", time.localtime()))
        global app_pics
        app_pics = self.win_app_pics
        self.log = log

    def create_cur_pic(self):
        self.log.info(f'create Windows app screenshot file: {self.win_app_pics}')
        if not os.path.exists(self.win_app_pics):
            os.mkdir(self.win_app_pics)

    def app_start(self):
        self.log.info('start app: %s', str(self.win_app_name))
        self.win_app = Application(backend="uia").start(self.win_app_path)

    def app_stop(self):
        self.log.info('stop app: %s', str(self.win_app_name))
        self.win_app[self.win_app_name].close()

    def shot_steps(self):
        if len(self.win_steps) > 0:
            self.log.info('start operate app')
            for step in self.win_steps:
                self.log.info(f'click {step[0]} at {step[1]}')
                self.win_app[step[0]][step[1]].click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        self.log.info(f'start screenshot Windows app: {operate_type}第{times}次.png')
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.win_app_pics, pic_name)
        self.win_app[self.win_app_name].set_focus().capture_as_image().save(pic_path)


class ScreenShotAndroidApp:
    """Android app"""

    def __init__(self, and_ip, and_port, and_name, and_steps, log):
        self.android_connect_info = and_ip + ':' + and_port
        self.and_name = and_name
        self.device = None
        self.and_steps = and_steps
        self.and_app_pics = os.path.join(pic_file, time.strftime("%Y%m%d%H%M%S", time.localtime()))
        self.logcat_path = ''
        self.logcat_file = None
        self.logcat = None
        global app_pics
        app_pics = self.and_app_pics
        self.log = log

    def create_cur_pic(self):
        self.log.info(f'create Android app screenshot file: {self.and_app_pics}')
        if not os.path.exists(self.and_app_pics):
            os.mkdir(self.and_app_pics)

    def app_start(self):
        self.device = u2.connect(self.android_connect_info)
        self.device.service('uiautomator').stop()
        # Maxim正常运行
        # stream模式，保证不会timeout导致杀掉，底层上是一个requests库提供的streaming 模式的response
        task = self.device.shell(
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
        self.device.service('uiautomator').start()
        self.device.set_fastinput_ime(True)  # 启用自动化定制的输入法，防止各机型输入法不同导致出错
        self.device.settings['operation_delay_methods'] = ['click', 'swipe', 'drag', 'press']
        # 设置隐式等待时间，默认20s
        self.device.implicitly_wait(20)
        with self.device.watch_context(builtin=True) as ctx:
            # 注意：这里不再对app内系统权限提示窗做监视
            ctx.when("^(下载|更新)").when("取消").click()  # 当同时出现（下载 或 更新）和 取消 按钮时，点击取消
            ctx.when("跳过%").click()
            ctx.when("继续").click()
            ctx.when("每次开启").click()
            ctx.when("创建").when("取消").click()
            ctx.when("恢复").when("取消").click()
            ctx.wait_stable(seconds=0.5)  # 开启弹窗监控，并等待界面稳定（两个弹窗检查周期内没有弹窗代表稳定）

        self.logcat_path = os.path.join(self.and_app_pics, 'logcat')
        if not os.path.exists(self.logcat_path):  # 判断地址是否存在，否则就新建
            os.makedirs(self.logcat_path)
        logcat_filename = os.path.join(self.logcat_path,
                                       time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.txt')
        self.logcat_file = open(logcat_filename, 'w')
        os.system(f'adb -s {self.android_connect_info} logcat -c')  # 清除所有日志缓存信息
        self.logcat = subprocess.Popen(f'adb -s {self.android_connect_info} logcat -v time',
                                       stdout=self.logcat_file, stderr=subprocess.PIPE)  # 开子进程将日志输出到指定文件
        self.log.info('start capturing log: %s', str(self.logcat_file))
        self.log.info('start app: %s', str(self.and_name))
        self.device.app_start(self.and_name, wait=True)

    def app_stop(self):
        self.logcat_file.close()
        self.logcat.terminate()  # 停止日志捕获
        self.log.info('stop capturing log')
        self.log.info('stop app: %s', str(self.and_name))
        self.device.app_stop(self.and_name)

    def shot_steps(self):
        self.log.info('start operate app')
        if len(self.and_steps) > 0:
            for step in self.and_steps:
                if step[2] == '':
                    step[2] = 0
                self.log.info(f'click {step[0]} at {step[1]}')
                self.device(**{step[0]: step[1]}).click()
                time.sleep(step[2]) if step[2] != '' else time.sleep(2)

    def screen_shot(self, operate_type, times):
        self.log.info(f'start screenshot Android app: {operate_type}第{times}次.png')
        pic_name = f'{operate_type}第{times}次.png'
        pic_path = os.path.join(self.and_app_pics, pic_name)
        self.device.screenshot(pic_path)


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
