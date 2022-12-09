from rest_framework.response import Response
from server.util.constant_util import *


def build_response(code=CODE_SUCCESS, msg='操作成功', data=''):
    return Response({'code': code, 'msg': msg, 'data': data})
