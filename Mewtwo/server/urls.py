#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/12/8 18:34
from django.urls import path

from server.views.mind_map import *
from server.views.jump import *
from server.views.user import *
from server_auth.lib.auth import *

urlpatterns = [
    # ---------------------------------------------------
    path('', to_dashboard),  # 跳转列表界面
    path('2_d', to_detail),  # 跳转详情界面
    path('s_2_d', share_to_detail),  # 从分享链接跳转详细界面
    path('2_share', to_share),  # 到分享界面
    path('2_star', to_star),  # 到收藏界面
    path('2_recycle', to_recycle),  # 回收站
    path(r'jsmind_op', JsMindLogView.as_view()),  # 更新快照，get日志操作

    # ---------------------------------------------------
    path('create', JsMindView.as_view()),  # 创建思维导图
    path('list', JsMindView.as_view()),  # 查询思维导图
    path('d', JsMindView.as_view()),  # 获得导图详情
    path('s_d', JsMindShareView.as_view()),  # 获得导图详情
    path('delete', JsMindView.as_view()),  # 删除思维导图
    path('delete_cancel', JsMindView.as_view()),  # 思维导图恢复
    path('share', JsMindShareView.as_view()),  # 分享思维导图，查询等
    path('star', JsMindStarView.as_view()),  # 收藏思维导图

    # ---------------------------------------------------
    path('register', MindUserView.as_view()),  # 用户注册
    path('login', LoginView.as_view()),  # 用户登录
    path('logout', LogoutView.as_view()),  # 用户登出

    # ---------------------------------------------------
]

