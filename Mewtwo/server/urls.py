#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/12/8 18:34
from django.urls import path

from server.views.views import index

urlpatterns = [
    # path(route, view, kwargs, name) 将route与view绑定
    path('', index, name='index'),
]
