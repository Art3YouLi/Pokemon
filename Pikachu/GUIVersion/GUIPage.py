#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/2 17:18
import inspect
import ctypes
import logging
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from GUIFunction import ValidateInput

from GUIFunction import AutoControl

base_win_weight = 800
base_win_height = 550


def _async_raise(tid, exc_type):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc_type):
        exc_type = type(exc_type)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class BaseWin:
    """主窗口定义"""

    def __init__(self, master):
        self.root = master
        self.root.title('HotSwap TestTool')
        self.root.geometry(str(base_win_weight) + 'x' + str(base_win_height))
        self.root.resizable(width=False, height=False)
        HomePage(self.root)


class HomePage:
    """主页面定义"""

    # 初始化页面，定义使用说明、使用前确认、功能按钮
    def __init__(self, master):
        self.master = master
        self.frm0 = None
        self.msg = '欢迎使用Hot Swap TestTool！！！\n' \
                   '当前版本号：v2.0.0\n' \
                   '正式开始使用前请注意：\n' \
                   '    1. 请确保继电器已成功连接至电脑并正确安装驱动！！！\n' \
                   '    2. 默认会先断开继电器！！！\n' \
                   '    3. 当前仅支持在Windows平台上使用！！！\n' \
                   '    4. 若需要截图安卓设备，请自行将设备通过无线连接方式连接至电脑！！！\n' \
                   '    5. 使用方式：\n' \
                   '        a. 双击运行\n' \
                   '        b. 确认阅读后勾选\n' \
                   '        c. 选择类型：\n' \
                   '            仅控制继电器且不需要截图\n' \
                   '            控制继电器并截图Windows App\n' \
                   '            控制继电器并截图Android App\n' \
                   '        d. 输入继电器控制相关参数\n' \
                   '        e. 若需要截图，输入app相关参数\n' \
                   '        f. 开始运行\n' \
                   '        g. 等待运行\n' \
                   '    6. 文件路径、继电器控制参数会做费控、字符串、数字校验\n' \
                   '    7. app信息（Windows app窗口名称、Android app包名）无法校验，请自行检查！！！\n' \
                   '\n' \
                   '若需要源码或有任何问题，请联系我zewen.fang@infisense.cn\n'
        self.ck_btn = None
        self.ck_btn_status = ttk.IntVar()
        self.btn_only = None
        self.btn_win = None
        self.btn_and = None

        self.page_frame()

    def page_frame(self):
        # 底层frame
        self.frm0 = ttk.Frame(self.master, padding=5)
        self.frm0.pack(fill=X, expand=YES, anchor=N)

        # 基准界面frame1 - 使用说明
        info_frm = ttk.Labelframe(self.frm0, text='Info', bootstyle='INFO')
        info_frm.pack(fill=BOTH, expand=YES, pady=10)
        textbox = ScrolledText(info_frm, padding=5, height=24, autohide=True, font='default 11 bold')
        textbox.pack(fill=BOTH, expand=YES)
        textbox.insert(END, self.msg)

        # 基准界面frame2 - 确认按钮
        ensure_frm = ttk.Frame(self.frm0)
        ensure_frm.pack(fill=X, expand=YES, pady=10)
        self.ck_btn = ttk.Checkbutton(ensure_frm, text="请确认您已阅读上述使用说明", bootstyle='INFO-round-toggle',
                                      variable=self.ck_btn_status, command=self.switch_btn_status)
        self.ck_btn.pack(side=RIGHT, padx=(15, 0))

        # 基准界面frame3 - 选择按钮
        btn_frm = ttk.Frame(self.frm0)
        btn_frm.pack(fill=X, expand=YES, pady=10)
        self.btn_only = ttk.Button(btn_frm, text='Only Control Relay', width=25, state='disabled',
                                   bootstyle='primary-outline',
                                   command=SwitchPage(self.master, 'nothing', self.frm0).switch_page)
        self.btn_only.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

        self.btn_win = ttk.Button(btn_frm, text='With Windows Application', width=25, state='disabled',
                                  bootstyle='success-outline',
                                  command=SwitchPage(self.master, 'windows', self.frm0).switch_page)
        self.btn_win.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

        self.btn_and = ttk.Button(btn_frm, text='With Android Application', width=25, state='disabled',
                                  bootstyle='warning-outline',
                                  command=SwitchPage(self.master, 'android', self.frm0).switch_page)
        self.btn_and.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

    # 根据确认复选框改变功能btn状态
    def switch_btn_status(self):
        if self.ck_btn_status.get() == 1:  # 判断是否被选中
            self.btn_only.configure(state='active')
            self.btn_win.configure(state='active')
            self.btn_and.configure(state='active')
        else:
            self.btn_only.configure(state='disabled')
            self.btn_win.configure(state='disabled')
            self.btn_and.configure(state='disabled')


class ShotPage:
    # 初始化参数配置页面
    def __init__(self, master, shot_type):
        # 初始化部分变量
        self.master = master
        self.shot_type = shot_type
        self.vi = ValidateInput()

        self.win_columns = ['窗口名称', '按钮名称', '等待时间(s)']
        self.and_columns = ['属性', '值', '等待时间(s)']

        # 输入参数变量
        self.control_num = None
        self.control_duration = None
        self.control_times = None

        self.tree_view = None

        self.win_app_path = None
        self.win_app_name = None

        self.and_ip = None
        self.and_port = None
        self.and_name = None

        # register the validation callback
        self.digit_func = self.master.register(self.vi.validate_number)
        self.alpha_func = self.master.register(self.vi.validate_alpha)
        self.ip_func = self.master.register(self.vi.validate_ip)
        self.file_func = self.master.register(self.vi.validate_file)

        # 底层frame
        self.frm0 = ttk.Frame(self.master, padding=5)
        self.frm0.pack(fill=X, expand=YES, anchor=N)

        # 参数部分
        # 继电器参数
        self.relay_frame()
        # app参数frame
        self.app_frame()

        # 控制按钮
        self.btn_frame()

    # 继电器参数
    def relay_frame(self):
        relay_frm = ttk.LabelFrame(self.frm0, text='Relay Parameters', padding=5, bootstyle='primary')
        relay_frm.pack(fill=X, expand=YES, pady=5, padx=5)

        num_frm = ttk.Frame(relay_frm)
        num_frm.pack(fill=X, expand=YES, pady=5)
        num_lbl = ttk.Label(num_frm, text='继电器序号', width=15)
        num_lbl.pack(side=LEFT, padx=(10, 0))
        self.control_num = ttk.Entry(num_frm, validate="focusout", validatecommand=(self.digit_func, '%P'))
        self.control_num.pack(side=LEFT, fill=X, expand=YES, padx=5)

        time_frm = ttk.Frame(relay_frm)
        time_frm.pack(fill=X, expand=YES, pady=5)
        time_lbl = ttk.Label(time_frm, text='闭合断开间隔(s)', width=15)
        time_lbl.pack(side=LEFT, padx=(10, 0))
        self.control_duration = ttk.Entry(time_frm, validate="focusout", validatecommand=(self.digit_func, '%P'))
        self.control_duration.pack(side=LEFT, fill=X, expand=YES, padx=5)

        times_frm = ttk.Frame(relay_frm)
        times_frm.pack(fill=X, expand=YES, pady=5)
        times_lbl = ttk.Label(times_frm, text='闭合断开次数', width=15)
        times_lbl.pack(side=LEFT, padx=(10, 0))
        self.control_times = ttk.Entry(times_frm, validate="focusout", validatecommand=(self.digit_func, '%P'))
        self.control_times.pack(side=LEFT, fill=X, expand=YES, padx=5)

    # app参数
    def app_frame(self):
        shot_frame = None
        if self.shot_type == 'windows':
            shot_frame = ttk.LabelFrame(self.frm0, text='Windows App Parameters', padding=5, bootstyle='success')
            shot_frame.pack(fill=X, expand=YES, pady=5, padx=5)

            path_frm = ttk.Frame(shot_frame)
            path_frm.pack(fill=X, expand=YES, pady=5)
            path_lbl = ttk.Label(path_frm, text='App路径(.exe)', width=15)
            path_lbl.pack(side=LEFT, padx=(10, 0))
            self.win_app_path = ttk.Entry(path_frm, textvariable='win_app_path',
                                          validate="focusout", validatecommand=(self.file_func, '%P'))
            self.win_app_path.pack(side=LEFT, fill=X, expand=YES, padx=5)
            btn = ttk.Button(path_frm, text='Browse', command=lambda: self.get_exe_path('win_app_path'), width=8)
            btn.pack(side=LEFT, padx=5)

            name_frm = ttk.Frame(shot_frame)
            name_frm.pack(fill=X, expand=YES, pady=5)
            name_lbl = ttk.Label(name_frm, text='主窗口名称', width=15)
            name_lbl.pack(side=LEFT, padx=(10, 0))
            self.win_app_name = ttk.Entry(name_frm)
            self.win_app_name.pack(side=LEFT, fill=X, expand=YES, padx=5)

        elif self.shot_type == 'android':
            shot_frame = ttk.LabelFrame(self.frm0, text='Android App Parameters', padding=5, bootstyle='warning')
            shot_frame.pack(fill=X, expand=YES, pady=5, padx=5)

            info_frm = ttk.Frame(shot_frame)
            info_frm.pack(fill=X, expand=YES, pady=5)
            ip_lbl = ttk.Label(info_frm, text='设备ip', width=15)
            ip_lbl.pack(side=LEFT, padx=(10, 0))
            self.and_ip = ttk.Entry(info_frm, validate="focusout", validatecommand=(self.ip_func, '%P'))
            self.and_ip.pack(side=LEFT, fill=X, expand=YES, padx=5)
            port_lbl = ttk.Label(info_frm, text='port', width=15)
            port_lbl.pack(side=LEFT, padx=(10, 0))
            self.and_port = ttk.Entry(info_frm, validate="focusout", validatecommand=(self.digit_func, '%P'))
            self.and_port.pack(side=LEFT, fill=X, expand=YES, padx=5)

            name_frm = ttk.Frame(shot_frame)
            name_frm.pack(fill=X, expand=YES, pady=5)
            name_lbl = ttk.Label(name_frm, text='测试包名', width=15)
            name_lbl.pack(side=LEFT, padx=(10, 0))
            self.and_name = ttk.Entry(name_frm)
            self.and_name.pack(side=LEFT, fill=X, expand=YES, padx=5)

        if self.shot_type != 'nothing':
            # Treeview
            step_frm = ttk.Frame(shot_frame)
            step_frm.pack(fill=X, expand=YES, pady=5)
            step_lbl = ttk.Label(step_frm, text='App出图步骤', width=15)
            step_lbl.pack(side=LEFT, padx=(10, 0))

            canvas = ttk.Canvas(step_frm)
            canvas.pack(side=LEFT, fill=X, expand=YES, padx=5)
            # 创建表格
            self.tree_view = ttk.Treeview(canvas, show='headings', height=8)
            self.tree_view.configure(columns=tuple(self.win_columns))
            for col in self.win_columns:
                self.tree_view.column(col, stretch=False, width=180)
            for col in self.tree_view['columns']:
                self.tree_view.heading(col, text=col.title(), anchor=W)
            self.tree_view.pack(side=LEFT, fill=X, expand=YES, padx=5)

            vbar = ttk.Scrollbar(canvas, orient=VERTICAL, command=self.tree_view.yview)
            self.tree_view.configure(yscrollcommand=vbar.set)
            self.tree_view.grid(row=0, column=0, sticky=NSEW)
            vbar.grid(row=0, column=1, sticky=NS)

            btn_frm = ttk.Frame(step_frm)
            btn_frm.pack(side=LEFT, fill=Y, expand=YES)
            btn_add = ttk.Button(btn_frm, text='Add', width=8, bootstyle='success', command=self.add_steps)
            btn_add.pack(expand=YES, padx=5)
            btn_del = ttk.Button(btn_frm, text='Del', width=8, bootstyle='DANGER', command=self.delete_steps)
            btn_del.pack(expand=YES, padx=5)

    # 功能按钮
    def btn_frame(self):
        btn_frm = ttk.Frame(self.frm0, padding=10)
        btn_frm.pack(fill=X, anchor='n', expand=YES)
        buttons = [
            ttk.Button(master=btn_frm, text='Start Executing', width=10,
                       bootstyle='SUCCESS-outline', command=self.start),
            ttk.Button(master=btn_frm, text='Reset Parameters', width=10,
                       bootstyle='DANGER-outline', command=self.reset),
            ttk.Button(master=btn_frm, text='Back to Home', width=10, bootstyle='INFO-outline',
                       command=SwitchPage(self.master, 'home', self.frm0).switch_page)]
        for button in buttons:
            button.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)

    # 获取路径
    def get_exe_path(self, path_name):
        self.master.update_idletasks()
        d = filedialog.askopenfilename()
        if d:
            self.master.setvar(path_name, d)
            self.win_app_path.focus()

    # 增加自定义出图步骤
    def add_steps(self):
        cur_columns = None
        if self.shot_type == 'windows':
            cur_columns = self.win_columns
        elif self.shot_type == 'android':
            cur_columns = self.and_columns
        # 直接在已有数据后填充
        self.pop_win_input(cur_columns)

    # 删除自定义出图步骤
    def delete_steps(self):
        cur_date = self.tree_view.get_children()
        if len(cur_date) >= 1:
            self.tree_view.delete(cur_date[0])

    # 自定义出图步骤输入弹窗
    def pop_win_input(self, columns):
        pop_win = ttk.Toplevel()
        pop_win.title('出图步骤参数')
        pop_win.geometry("360x280+200+200")  # 定义弹窗大小及位置，前两个是大小，用字母“x”连接，后面是位置。
        pop_win.resizable(width=False, height=False)
        data = []
        entry_lst = []
        for i in range(len(columns)):
            frm = ttk.Frame(pop_win)
            frm.pack(fill=X, expand=YES, pady=5)
            lbl = ttk.Label(frm, text=columns[i], width=10)
            lbl.pack(side=LEFT, padx=(10, 0))
            entry = ttk.Entry(frm)
            entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
            if i == 0:
                entry.focus_set()  # 把焦点设置到输入框上，就是弹窗一出，光标在输入框里了。
            entry_lst.append(entry)

        def deal_data():  # 定义处理方法
            for ent in entry_lst:
                data.append(ent.get())
            pop_win.destroy()  # 关闭弹窗
            idd = self.tree_view.insert('', 0, values=tuple(data))
            self.tree_view.see(idd)
            self.tree_view.update()

        def exit_pop_win():
            pop_win.destroy()  # 关闭弹窗

        pop_win.bind("<Escape>", exit_pop_win)  # 当焦点在整个弹窗上时，绑定ESC退出

        btn_frm = ttk.Frame(pop_win, padding=10)
        btn_frm.pack(fill=X, anchor='s', expand=YES)
        buttons = [ttk.Button(master=btn_frm, text="Exit", width=10, bootstyle='DANGER-outline', command=exit_pop_win),
                   ttk.Button(master=btn_frm, text="Submit", width=10, bootstyle='SUCCESS-outline', command=deal_data)]
        for button in buttons:
            button.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)

    # 开始执行
    def start(self):
        validate_flag = self.control_num.validate() and self.control_duration.validate() \
                        and self.control_times.validate()
        if self.shot_type == 'windows':
            validate_flag = validate_flag and self.win_app_path.validate() and self.win_app_name.validate()
        elif self.shot_type == 'android':
            validate_flag = validate_flag and self.and_ip.validate() and self.and_port.validate() \
                            and self.and_name.validate()
        if validate_flag:
            app_data = {'shot_type': self.shot_type}
            if self.shot_type != 'nothing':
                steps = self.tree_view.get_children()
                app_data['steps'] = []
                if len(steps) > 0:
                    for line in self.tree_view.get_children():
                        line_data = self.tree_view.item(line)['values']
                        app_data['steps'].insert(0, line_data)
                if self.shot_type == 'windows':
                    app_data['app_path'] = self.win_app_path.get()
                    app_data['app_name'] = self.win_app_name.get()
                elif self.shot_type == 'android':
                    app_data['app_path'] = self.and_ip.get() + ':' + self.and_ip.get()
                    app_data['app_name'] = self.and_name.get()

            control_num = self.control_num.get()
            control_duration = self.control_duration.get()
            control_times = self.control_times.get()

            self.frm0.destroy()
            LogPage(self.master, control_num, control_duration, control_times, app_data)

        else:
            Messagebox.show_error(title='Error Msg', message='Input error or not, please check it！')

    # 重置参数
    def reset(self):
        self.control_num.delete(0, tk.END)
        self.control_duration.delete(0, tk.END)
        self.control_times.delete(0, tk.END)
        if self.shot_type != 'nothing':
            for i in self.tree_view.get_children():
                self.tree_view.delete(i)
            if self.shot_type == 'windows':
                self.win_app_path.delete(0, tk.END)
                self.win_app_name.delete(0, tk.END)
            elif self.shot_type == 'android':
                self.and_ip.delete(0, tk.END)
                self.and_port.delete(0, tk.END)
                self.and_name.delete(0, tk.END)


class LogPage:
    """log页面定义"""
    def __init__(self, master, control_num, control_duration, control_times, app_data):
        self.file_handler = None
        self.stream_handler = None
        self.master = master
        self.control_num = control_num
        self.control_duration = control_duration
        self.control_times = control_times
        self.app_data = app_data

        # 底层frame
        self.frm0 = ttk.Frame(self.master, padding=5)
        self.frm0.pack(fill=X, expand=YES, anchor=N)

        # 继电器控制软件参数部分
        self.log = None
        self.log_frame()

        # 控制按钮
        self.back_btn = None
        self.stop_btn = None
        self.btn_frame()

        # 执行启动
        time.sleep(0.5)
        self.ac_thread = None
        ac = AutoControl(self.log, control_num, control_duration, control_times, app_data)
        self.ac_thread = threading.Thread(target=ac.main_func, daemon=True)
        self.ac_thread.start()

    def log_frame(self):
        self.log = logging.getLogger('log')
        self.log.setLevel(logging.INFO)
        # 日志输出到屏幕
        stream_handler_box = LoggerBox(self.frm0)
        stream_handler_box.pack(fill=BOTH, expand=YES)
        self.stream_handler = logging.StreamHandler(stream_handler_box)

        # 日志保存到本地
        log_file = ''
        if getattr(sys, 'frozen', False):
            log_file = os.path.dirname(sys.executable)
        elif __file__:
            log_file = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(log_file, 'log')
        if not os.path.exists(log_file):
            os.mkdir(log_file)
        log_file = os.path.join(log_file, 'log.txt')
        if os.path.exists(log_file):
            os.remove(log_file)
        self.file_handler = logging.FileHandler(log_file, encoding='UTF-8')

        # 设置日志格式
        stream_formatter = logging.Formatter(
            '%(levelname)s %(asctime)s:  %(message)s')
        self.stream_handler.setFormatter(stream_formatter)
        file_formatter = logging.Formatter(
            '[%(levelname)s %(asctime)s %(filename)s:  %(lineno)d %(funcName)s]: %(message)s')
        self.file_handler.setFormatter(file_formatter)

        self.log.addHandler(self.stream_handler)
        self.log.addHandler(self.file_handler)

    def btn_frame(self):
        btn_frm = ttk.Frame(self.frm0, padding=10)
        btn_frm.pack(fill=X, anchor='s', expand=YES)
        self.stop_btn = ttk.Button(master=btn_frm, text='Stop Executing', width=10, bootstyle='DANGER-outline',
                                   command=self.stop_running)
        self.stop_btn.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)
        self.back_btn = ttk.Button(master=btn_frm, text='Back to Settings', width=10, bootstyle='INFO-outline',
                                   command=self.back_to_settings)
        self.back_btn.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)
        self.back_btn = ttk.Button(master=btn_frm, text='Back to Home', width=10, bootstyle='INFO-outline',
                                   command=self.back_to_home)
        self.back_btn.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)

    def back_to_settings(self):
        if self.ac_thread.is_alive():
            Messagebox.show_error(title='Error Msg', message='The program is running, please stop the thread first!')
        else:
            SwitchPage(self.master, self.app_data['shot_type'], self.frm0).switch_page()

    def stop_running(self):
        if self.ac_thread.is_alive():
            stop_thread(self.ac_thread)
            self.log.warning('Please note that the process is interrupted manually!')

    def back_to_home(self):
        if self.ac_thread.is_alive():
            Messagebox.show_error(title='Error Msg', message='The program is running, please stop the thread first!')
        else:
            SwitchPage(self.master, 'home', self.frm0).switch_page()


class SwitchPage:
    def __init__(self, master, page_name, page_frame: ttk.Frame):
        self.master = master
        self.page_frame = page_frame
        self.page_name = page_name

    def switch_page(self):
        self.page_frame.destroy()
        if self.page_name.lower() in ['windows', 'android', 'nothing']:
            ShotPage(self.master, self.page_name)
        elif self.page_name == 'home':
            HomePage(self.master)


class LoggerBox(ttk.ScrolledText):
    def write(self, message):
        self.insert("end", message)
        self.yview_moveto(1)
