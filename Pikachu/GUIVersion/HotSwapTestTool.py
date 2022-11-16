#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/15 11:44
import ttkbootstrap as ttk

from GUIPage import BaseWin


if __name__ == '__main__':
    root = ttk.Window(themename='superhero')
    BaseWin(root)
    root.mainloop()
