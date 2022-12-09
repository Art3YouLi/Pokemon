from django import http
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend  # 验证基类
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView

from server.util.constant_util import *
from server.util.mix_util import build_response


class AuthBackend(ModelBackend):
    """
    login 方法会调用该方法
    """
    pass

    # 重写验证方式
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     user = MindUser.objects.get(id=1)
    #     if user is not None and user.check_password(password):
    #         return user


# 登录方式有多种
# 1、用户名密码登录：直接匹配数据库的用户名密码


# 2、微信扫码登录：1、生成带标记的二维码 2、用户扫码 3、微信通知服务器端 4、服务器校验是否有注册，如果没有注册则新增用户 5、服务器通知前端界面


# 3、手机号短信验证码登录 1、发送短信验证码 2、用户界面向服务器提交手机号和验证码  3、服务器请求短服务商  4、服务器校验是否有注册，如果没有注册则新增用户

class LoginView(APIView):
    """

    """

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # django内置认证来校验登录用户

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                # 记住登录状态
                login(request, user)
                return build_response(msg='登录成功')
            else:
                return build_response(code=CODE_FAILED, msg='登录失败')
        else:
            return build_response(code=CODE_FAILED, msg='登录失败')


class LogoutView(APIView):
    """
    注销
    """

    def get(self, request):
        logout(request)
        return build_response(msg='注销成功')

    def post(self, request):
        logout(request)
        return build_response(msg='注销成功')


class LoginRequiredJSONMixin(LoginRequiredMixin):
    """自定义LoginRequiredMixin
    如果用户未登录，响应JSON，且状态码为400
    """

    def handle_no_permission(self):
        # return build_response(code=CODE_FAILED, msg='用户未登录！')
        return http.JsonResponse({'code': CODE_FAILED, 'msg': '用户未登录'})
