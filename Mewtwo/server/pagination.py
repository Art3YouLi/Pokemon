#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ZeWen.Fang
# datetime:2022/12/9 14:09
from rest_framework.pagination import PageNumberPagination
from server.util.constant_util import *
from rest_framework.response import Response


class DefaultNumberPagination(PageNumberPagination):
    page_size = 1  # default page size
    page_size_query_param = 'page_size'  # ?page=xx&page_size=??
    max_page_size = 50  # max page size

    def get_paginated_response(self, data):
        """
        重写返回值格式
        """
        return Response({
            'code': CODE_SUCCESS,
            'count': self.page.paginator.count,
            'results': data
        })
