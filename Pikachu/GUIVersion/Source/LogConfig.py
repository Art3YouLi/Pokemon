#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/11/29 16:08
import logging
import os
import sys


class LogConfig:
    def __init__(self, log_level):
        self.log = logging.getLogger('Log')
        self.log.setLevel(log_level)

        # 日志保存到本地
        log_file = ''
        if getattr(sys, 'frozen', False):
            log_file = os.path.dirname(sys.executable)
        elif __file__:
            log_file = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(log_file, '../Log')
        if not os.path.exists(log_file):
            os.mkdir(log_file)
        log_file = os.path.join(log_file, 'Log.txt')
        # if os.path.exists(log_file):
        #     os.remove(log_file)

        self.stream_handler = logging.StreamHandler()
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
