#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/15 11:44
import logging
import ttkbootstrap as ttk

from Source.GUIPage import BaseWin
from Source.LogConfig import LogConfig


if __name__ == '__main__':
    log_config = LogConfig(logging.INFO)
    root = ttk.Window(themename='superhero')
    BaseWin(root, log_config)
    root.mainloop()
