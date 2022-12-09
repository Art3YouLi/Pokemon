#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/12/9 14:08
import django_filters
from django_filters import rest_framework

from server.models import *


class CooperationMindFilter(django_filters.rest_framework.FilterSet):
    """
    思维导图filter
    """
    coop_mind_name = rest_framework.CharFilter(field_name='coop_mind_name', lookup_expr='icontains')

    class Meta:
        model = CooperationMind
        fields = "__all__"


class CooperationMindShareFilter(django_filters.rest_framework.FilterSet):
    """
    思维导图分享filter
    """
    coop_mind_name = rest_framework.CharFilter(field_name='coop_mind_name', lookup_expr='icontains')

    class Meta:
        model = CooperationMindShare
        fields = "__all__"
