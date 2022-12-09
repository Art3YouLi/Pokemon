#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/12/9 14:10
from rest_framework import serializers
from server.models import *


class CooperationMindSerializer(serializers.ModelSerializer):
    """
    思维导图序列
    """

    class Meta:
        model = CooperationMind
        fields = '__all__'  # 包含模型类的所有字段


class CooperationMindLogSerializer(serializers.ModelSerializer):
    """
    思维导图日志序列
    """

    class Meta:
        model = CooperationMindLog
        fields = "__all__"


class CooperationMindShareSerializer(serializers.ModelSerializer):
    """
    思维导图分享序列
    """

    class Meta:
        model = CooperationMindShare
        fields = "__all__"
