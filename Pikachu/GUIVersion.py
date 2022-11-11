#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/2 17:18
import pathlib
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

base_win_weight = 800
base_win_height = 600


class BaseWin:
    def __init__(self, master):
        self.root = master
        self.root.title('热拔插测试小工具')
        self.root.geometry(str(base_win_weight) + 'x' + str(base_win_height))
        self.root.resizable(width=False, height=False)
        # BasePage(self.root)
        ShotPage(self.root, 'android')


class BasePage:
    def __init__(self, master):
        self.msg = '====================================================================\n' \
                   '欢迎使用Auto Control BMW8015！！！\n' \
                   '当前版本号：v1.0.1\n' \
                   '正式开始使用前请注意：\n' \
                   '    1. 请确保继电器已成功连接至电脑并正确安装驱动！！！\n' \
                   '    2. 请确保继电器控制软件8路.exe与当前exe文件在同一路径下！！！\n' \
                   '    3. 默认第一次断开继电器！！！\n' \
                   '    4. 使用方式：\n' \
                   '        a. 满足上述条件后双击运行\n' \
                   '        b. 输入需要控制的继电器序号后回车\n' \
                   '        c. 输入闭合断开继电器时间间隔后回车\n' \
                   '        d. 输入需要重复闭合断开次数后回车（闭合断开为1次）\n' \
                   '        e. 选择需要截图设备类型\n' \
                   '        f. 输入需要被截图app信息\n' \
                   '        g. 等待运行\n' \
                   '    5. 每次输入仅有3次机会！！！\n' \
                   '    6. app信息（Windows app窗口名称、Android app包名）无法校验，请自行检查！！！\n' \
                   '    7. 详细使用说明请查看附带README.md文档！！！\n' \
                   '若需要源码或有任何问题，请联系我zewen.fang@infisense.cn'
        self.status = ttk.IntVar()
        self.master = master

        # 底层frame
        self.frm0 = ttk.Frame(self.master, padding=5)
        self.frm0.pack(fill=X, expand=YES, anchor=N)

        # 基准界面frame1 - 使用说明
        info_frm = ttk.Labelframe(self.frm0, text='Info', bootstyle='INFO')
        info_frm.pack(fill=BOTH, expand=YES, pady=10)
        textbox = ScrolledText(info_frm, padding=5, height=20, autohide=True, font='Verdana 10 bold')
        textbox.pack(fill=BOTH, expand=YES)
        textbox.insert(END, self.msg)

        # 基准界面frame2 - 确认按钮
        ensure_frm = ttk.Frame(self.frm0)
        ensure_frm.pack(fill=X, expand=YES, pady=10)
        self.ck_btn = ttk.Checkbutton(ensure_frm, text="请确认您已阅读上述使用说明", bootstyle='INFO-round-toggle',
                                      variable=self.status, command=self.enable_btn)
        self.ck_btn.pack(side=RIGHT, padx=(15, 0))

        # 基准界面frame3 - 选择按钮
        btn_frm = ttk.Frame(self.frm0)
        btn_frm.pack(fill=X, expand=YES, pady=10)
        self.btn_only = ttk.Button(btn_frm, text='仅控制继电器', width=25, state='disabled',
                                   bootstyle='primary-outline', command=self.goto_shot_nothing)
        self.btn_only.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

        self.btn_win = ttk.Button(btn_frm, text='with Windows Application', width=25, state='disabled',
                                  bootstyle='success-outline', command=self.goto_shot_win)
        self.btn_win.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

        self.btn_and = ttk.Button(btn_frm, text='with Android Application', width=25, state='disabled',
                                  bootstyle='warning-outline', command=self.goto_shot_And)
        self.btn_and.pack(side=LEFT, fill=X, expand=YES, pady=10, padx=5)

    def enable_btn(self):
        if self.status.get() == 1:  # 判断是否被选中
            self.btn_only.configure(state='active')
            self.btn_win.configure(state='active')
            self.btn_and.configure(state='active')
        else:
            self.btn_only.configure(state='disabled')
            self.btn_win.configure(state='disabled')
            self.btn_and.configure(state='disabled')

    def goto_shot_win(self):
        self.frm0.destroy()
        ShotPage(self.master, 'windows')

    def goto_shot_And(self):
        self.frm0.destroy()
        ShotPage(self.master, 'android')

    def goto_shot_nothing(self):
        self.frm0.destroy()
        ShotPage(self.master, 'nothing')


class ShotPage:
    def __init__(self, master, shot_type):
        self.parameter_frm = None
        self.master = master
        self.shot_type = shot_type

        # 底层frame
        self.frm0 = ttk.Frame(self.master, padding=5)
        self.frm0.pack(fill=X, expand=YES, anchor=N)

        # 参数输入
        self.parameter_frm = ttk.Frame(self.frm0)
        self.parameter_frm.pack(fill=BOTH, pady=10)
        self.create_control_frame()
        if self.shot_type == 'windows':
            self.shot_win()
        elif self.shot_type == 'android':
            self.shot_android()

        # 控制按钮
        self.create_btn_frame()

    def create_control_frame(self):
        _path = pathlib.Path().absolute().as_posix()
        path_var = ttk.StringVar(value=_path)
        num_var = ttk.StringVar(value='6')

        # 继电器参数
        relay_frm = ttk.LabelFrame(self.parameter_frm, text='继电器参数', padding=5, bootstyle='primary')
        relay_frm.pack(fill=X, expand=YES, pady=5, padx=5)

        path_frm = ttk.Frame(relay_frm)
        path_frm.pack(fill=X, expand=YES, pady=5)
        path_lbl = ttk.Label(path_frm, text='继电器路径', width=10)
        path_lbl.pack(side=LEFT, padx=(10, 0))
        file_entry = ttk.Entry(path_frm, textvariable=path_var)
        file_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        btn = ttk.Button(path_frm, text='Browse', command=self.get_directory, width=8)
        btn.pack(side=LEFT, padx=5)

        num_frm = ttk.Frame(relay_frm)
        num_frm.pack(fill=X, expand=YES, pady=5)
        num_lbl = ttk.Label(num_frm, text='控制序号', width=10)
        num_lbl.pack(side=LEFT, padx=(10, 0))
        num_entry = ttk.Entry(num_frm, textvariable=num_var)
        num_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        time_frm = ttk.Frame(relay_frm)
        time_frm.pack(fill=X, expand=YES, pady=5)
        time_lbl = ttk.Label(time_frm, text='间隔时间(s)', width=10)
        time_lbl.pack(side=LEFT, padx=(10, 0))
        time_entry = ttk.Entry(time_frm)
        time_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        times_frm = ttk.Frame(relay_frm)
        times_frm.pack(fill=X, expand=YES, pady=5)
        times_lbl = ttk.Label(times_frm, text='操作次数', width=10)
        times_lbl.pack(side=LEFT, padx=(10, 0))
        times_entry = ttk.Entry(times_frm)
        times_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

    def create_btn_frame(self):
        btn_frm = ttk.Frame(self.frm0, padding=10)
        btn_frm.pack(fill=X, anchor='s', expand=YES)
        buttons = [ttk.Button(master=btn_frm, text="开始执行", width=10, bootstyle='INFO-outline', command=self.start),
                   ttk.Button(master=btn_frm, text="重置参数", width=10, bootstyle='SUCCESS-outline', command=self.reset),
                   ttk.Button(master=btn_frm, text="返回首页", width=10, bootstyle='DANGER-outline', command=self.back)]
        for button in buttons:
            button.pack(side=LEFT, fill=X, expand=YES, pady=5, padx=5)

    def shot_win(self):
        _path = pathlib.Path().absolute().as_posix()
        path_var = ttk.StringVar(value=_path)
        # win app参数
        win_frm = ttk.LabelFrame(self.parameter_frm, text='Windows App参数', padding=5, bootstyle='success')
        win_frm.pack(fill=X, expand=YES, pady=5, padx=5)

        path_frm = ttk.Frame(win_frm)
        path_frm.pack(fill=X, expand=YES, pady=5)
        path_lbl = ttk.Label(path_frm, text='App路径', width=10)
        path_lbl.pack(side=LEFT, padx=(10, 0))
        file_entry = ttk.Entry(path_frm, textvariable=path_var)
        file_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        btn = ttk.Button(path_frm, text='Browse', command=self.get_directory, width=8)
        btn.pack(side=LEFT, padx=5)

        name_frm = ttk.Frame(win_frm)
        name_frm.pack(fill=X, expand=YES, pady=5)
        name_lbl = ttk.Label(name_frm, text='主窗口名称', width=10)
        name_lbl.pack(side=LEFT, padx=(10, 0))
        name_entry = ttk.Entry(name_frm)
        name_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        # Treeview
        step_frm = ttk.Frame(win_frm)
        step_frm.pack(fill=X, expand=YES, pady=5)
        step_lbl = ttk.Label(step_frm, text='出图步骤', width=10)
        step_lbl.pack(side=LEFT, padx=(10, 0))
        tv = ttk.Treeview(step_frm, show='headings', height=8)
        tv.configure(columns=('当前窗口名称', '按钮名称', '索引'))
        for col in ['当前窗口名称', '按钮名称', '索引']:
            tv.column(col, stretch=False)
        for col in tv['columns']:
            tv.heading(col, text=col.title(), anchor=W)
        tv.pack(side=LEFT, fill=X, expand=YES, padx=5)

        btn_frm = ttk.Frame(step_frm)
        btn_frm.pack(side=LEFT, fill=Y, expand=YES)
        btn_add = ttk.Button(btn_frm, text='Add+', width=8, bootstyle='success')
        btn_add.pack(expand=YES, padx=5)
        btn_del = ttk.Button(btn_frm, text='Delete', width=8, bootstyle='DANGER')
        btn_del.pack(expand=YES, padx=5)

    def shot_android(self):
        # win app参数
        and_frm = ttk.LabelFrame(self.parameter_frm, text='Android App参数', padding=5, bootstyle='warning')
        and_frm.pack(fill=X, expand=YES, pady=5, padx=5)

        info_frm = ttk.Frame(and_frm)
        info_frm.pack(fill=X, expand=YES, pady=5)
        ip_lbl = ttk.Label(info_frm, text='设备ip', width=10)
        ip_lbl.pack(side=LEFT, padx=(10, 0))
        ip_entry = ttk.Entry(info_frm)
        ip_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        port_lbl = ttk.Label(info_frm, text='port', width=10)
        port_lbl.pack(side=LEFT, padx=(10, 0))
        port_entry = ttk.Entry(info_frm)
        port_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        name_frm = ttk.Frame(and_frm)
        name_frm.pack(fill=X, expand=YES, pady=5)
        name_lbl = ttk.Label(name_frm, text='测试包名', width=10)
        name_lbl.pack(side=LEFT, padx=(10, 0))
        name_entry = ttk.Entry(name_frm)
        name_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)

        # Treeview
        step_frm = ttk.Frame(and_frm)
        step_frm.pack(fill=X, expand=YES, pady=5)
        step_lbl = ttk.Label(step_frm, text='出图步骤', width=10)
        step_lbl.pack(side=LEFT, padx=(10, 0))
        tv = ttk.Treeview(step_frm, show='headings', height=8)
        tv.configure(columns=('属性', '值', '索引'))
        for col in ['属性', '值', '索引']:
            tv.column(col, stretch=False)
        for col in tv['columns']:
            tv.heading(col, text=col.title(), anchor=W)
        tv.pack(side=LEFT, fill=X, expand=YES, padx=5)

        btn_frm = ttk.Frame(step_frm)
        btn_frm.pack(side=LEFT, fill=Y, expand=YES)
        btn_add = ttk.Button(btn_frm, text='Add+', width=8, bootstyle='success')
        btn_add.pack(expand=YES, padx=5)
        btn_del = ttk.Button(btn_frm, text='Delete', width=8, bootstyle='DANGER')
        btn_del.pack(expand=YES, padx=5)

    def get_directory(self):
        pass

    def back(self):
        self.frm0.destroy()
        BasePage(self.master)

    def start(self):
        pass

    def reset(self):
        pass


if __name__ == '__main__':
    root = ttk.Window(themename='superhero')
    BaseWin(root)
    root.mainloop()
