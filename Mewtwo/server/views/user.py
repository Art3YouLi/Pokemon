from django.http.response import JsonResponse
from rest_framework.views import APIView

from server.util.mix_util import build_response
from server_auth.models import MindUser


class MindUserView(APIView):
    """
    用户注册
    """

    def post(self, request):
        data_dict = request.POST
        user_name = data_dict.get('userName')
        input_password = data_dict.get('inputPassword')
        print('userName:%s,inputPassword:%s' % (user_name, input_password))

        # 根据用户名查询 MindUser
        db_user = MindUser.objects.filter(username=user_name).first()
        if db_user is not None:
            return build_response(code=-1, msg='用户名：%s 已经存在，请更换！' % user_name)

        MindUser.objects.create_user(username=user_name, password=input_password, email='')
        return JsonResponse({"code": 0, "msg": "注册成功，跳转登录界面中"})
