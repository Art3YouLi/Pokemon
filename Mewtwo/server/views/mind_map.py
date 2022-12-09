import uuid
from datetime import datetime as dt

from django_filters.rest_framework import *
from rest_framework.generics import *
from rest_framework.views import APIView

from server.filters import *
from server.pagination import DefaultNumberPagination
from server.serializers import *
from server.util.constant_util import *
from server.util.mix_util import build_response
from server_auth.lib.auth import LoginRequiredJSONMixin
from django.db.models import Exists, OuterRef


class JsMindView(LoginRequiredJSONMixin, ListAPIView):
    """
    思维导图view
    """
    queryset = CooperationMind.objects.all()
    serializer_class = CooperationMindSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = CooperationMindFilter
    pagination_class = DefaultNumberPagination

    def get(self, request, *args, **kwargs):
        """
        查询思维导图
        """
        pk = request.GET.get('id')
        # 页面源
        page_tag = request.GET.get('s_p')
        user = request.user
        if page_tag is None or user.id is None:
            return build_response(code=CODE_FAILED, msg="参数错误")

        print('list current user: %s' % user)
        if pk is not None:
            # 查询导图详细 查看用户是否有权限
            sql = """
            select * from cooperation_mind mind where id=%s and mind.creator_user_id=%s 
            union all select m1.* from cooperation_mind m1 join cooperation_mind_share sh on sh.coop_mind_id  = m1.id where m1.id=%s and sh.operator_user_id =%s
            union all select m1.* from cooperation_mind m1 join cooperation_mind_star st on st.coop_mind_id  = m1.id where m1.id=%s and st.operator_user_id =%s
            """ % (pk, user.id, pk, user.id, pk, user.id)
            mind = CooperationMind.objects.raw(sql)
            if len(mind) is None:
                return build_response(code=CODE_FAILED, msg="无权限")
            # 序列化
            serializer = CooperationMindSerializer(mind[0])
            return build_response(data=serializer.data)

        # 查询列表
        if 'b9b101e' == page_tag:
            # 我的文件
            self.queryset = CooperationMind.objects.filter(creator_user_id=user.id, deleted=0).values('id', 'coop_mind_name', "client_uuid", "data_format")
        elif 'share' == page_tag:
            # 我的分享
            share = CooperationMindShare.objects.filter(coop_mind_id=OuterRef('id'), operator_user_id=user.id)
            self.queryset = CooperationMind.objects.annotate(share_col=Exists(share), ).filter(share_col=1, deleted=0).values('id', 'coop_mind_name', "client_uuid", "data_format")
        elif 'star' == page_tag:
            # 我的收藏
            star = CooperationMindStar.objects.filter(coop_mind_id=OuterRef('id'), operator_user_id=user.id)
            self.queryset = CooperationMind.objects.annotate(star_col=Exists(star), ).filter(star_col=1, deleted=0).values('id', 'coop_mind_name', "client_uuid", "data_format")
        elif 'recycle' == page_tag:
            # 回收站
            self.queryset = CooperationMind.objects.filter(creator_user_id=user.id, deleted=1).values('id', 'coop_mind_name', "client_uuid", "data_format")
        else:
            # 不返回数据
            self.queryset = CooperationMind.objects.filter(creator_user_id=-100).values('id', 'coop_mind_name', "client_uuid", "data_format")
        return self.list(request, *args, **kwargs)

    def post(self, request):
        """
        创建思维导图
        """
        user = request.user
        coop_mind_name = request.data.get('mind_name')
        coop_mind_id = request.data.get('coop_mind_id')
        op_type = request.data.get('op_type')
        if op_type == "delete_cancel":
            CooperationMind.objects.filter(id=coop_mind_id, creator_user_id=user.id).update(deleted=False)
            return build_response()
        else:
            user = request.user
            data_format = 'node_tree'
            mind = CooperationMind(coop_mind_name=coop_mind_name, client_uuid='', mind_log_id=-1, creator_user_id=user.id, snapshot_data=SNAPSHOT_JSON_DATA, data_format=data_format)
            mind.save()
            return build_response(data=mind.id)

    def delete(self, request):
        # 删除
        pk = request.POST.get('coop_mind_id')
        source = request.POST.get('source')
        user = request.user
        res = None
        if source == 'dashboard':
            res = CooperationMind.objects.filter(id=pk, creator_user_id=user.id).update(deleted=True)
        elif source == 'recycle':
            res = CooperationMind.objects.filter(id=pk, creator_user_id=user.id).delete()
        print(res)
        return build_response(msg='删除成功')


# Create your views here.
class JsMindLogView(APIView):
    """
    日志获取，快照保存
    """

    def get(self, request):
        """
        查询日志
        """
        param = request.GET
        coop_mind_id = param.get('coop_mind_id')
        cooperation_mind_log_id = param.get('cooperation_mind_log_id')
        query_set = CooperationMindLog.objects.filter(coop_mind_id=coop_mind_id, id__gt=cooperation_mind_log_id)
        log_list = CooperationMindLogSerializer(query_set, many=True)
        return build_response(data=log_list.data)

    def post(self, request):
        """
        更新保存快照
        """

        post_body = request.POST
        client_uuid = post_body.get('client_uuid')
        type = post_body.get('type')
        if 'snapshot' == type:
            # 保存快照
            coop_mind_id = post_body.get('coop_mind_id')
            data = post_body.get('data')
            coop_mind_log_id = post_body.get('coop_mind_log_id')
            data_format = post_body.get('data_format')
            CooperationMind.objects.filter(id=coop_mind_id, mind_log_id__lt=coop_mind_log_id).update(data_format=data_format, snapshot_data=data, mind_log_id=coop_mind_log_id, update_time=dt.now(), client_uuid=client_uuid)
        return build_response()


class JsMindShareView(LoginRequiredJSONMixin, ListAPIView):
    """
    思维导图分享view
    """
    serializer_class = CooperationMindShareSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = CooperationMindShareFilter
    pagination_class = DefaultNumberPagination

    def get(self, request, *args, **kwargs):
        """
        通过链接即uuid、hash获得分享的导图详情
        """
        share_uuid_hash = request.GET.get('h')
        share_uuid = request.GET.get('u')
        coop_mind_id = request.GET.get('coop_mind_id')
        user = request.user
        if user.id is None:
            return build_response(code=CODE_FAILED, msg="用户未登录")
        #
        if share_uuid_hash is not None and share_uuid is not None:
            share = CooperationMindShare.objects.filter(share_uuid_hash=share_uuid_hash, share_uuid=share_uuid).first()
            if share is None:
                return build_response(code=CODE_FAILED, msg='分享不存在')

            # 查询mind
            mind = CooperationMind.objects.filter(id=share.coop_mind_id).first()
            serializer = CooperationMindSerializer(mind)
            return build_response(data=serializer.data)
        elif coop_mind_id is not None:
            # 获得分享链接
            share = CooperationMindShare.objects.filter(operator_user_id=user.id, coop_mind_id=coop_mind_id).first()
            if share is None:
                return build_response(code=CODE_FAILED, msg='分享不存在')
            serializer = CooperationMindShareSerializer(share)
            return build_response(data=serializer.data)
        else:
            # 查询列表
            self.queryset = CooperationMindShare.objects.filter(operator_user_id=user.id).all()
            return self.list(request, *args, **kwargs)

    def post(self, request):
        """
        分享脑图功能，只有创建人能分享
        """
        post_body = request.POST
        id = post_body.get('id')
        user = request.user
        if id is None:
            return build_response(code=CODE_FAILED, msg='参数错误')
        mind = CooperationMind.objects.filter(id=id, creator_user_id=user.id).first()
        if mind is None:
            return build_response(code=CODE_FAILED, msg='导图不存在')

        # 校验成功
        share = CooperationMindShare.objects.filter(coop_mind_id=mind.id, operator_user_id=user.id).first()
        if share is None:
            uuid_str = str(uuid.uuid4()).replace('-', "")
            share_uuid_hash = -1
            share = CooperationMindShare(coop_mind_id=mind.id, coop_mind_name=mind.coop_mind_name, share_uuid=uuid_str, share_uuid_hash=share_uuid_hash, operator_user_id=user.id)
            share.save()
            return build_response(data={"u": uuid_str, "h": share_uuid_hash})

        # 重复分享
        return build_response(code=DUPLICATE, data={"u": share.share_uuid, "h": share.share_uuid_hash})

    def delete(self, request):
        """

        """
        post_body = request.POST
        id = post_body.get('id')
        user = request.user
        if id is None:
            return build_response(code=CODE_FAILED, msg='参数错误')
        if user.id is None:
            return build_response(code=CODE_FAILED, msg='用户未登录')
        res = CooperationMindShare.objects.filter(coop_mind_id=id, operator_user_id=user.id).delete()
        return build_response(msg="操作成功", data=res[0])


class JsMindStarView(LoginRequiredJSONMixin, ListAPIView):
    """
    收藏
    """

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request):
        user = request.user
        post_body = request.POST
        # 思维导图id
        coop_mind_id = post_body.get('coop_mind_id')
        if coop_mind_id is None:
            return build_response(CODE_FAILED, msg="参数错误")

        mind = CooperationMind.objects.filter(id=coop_mind_id).first()
        if mind is None:
            return build_response(CODE_FAILED, msg="导图不存在")

        star = CooperationMindStar.objects.filter(operator_user_id=user.id, coop_mind_id=coop_mind_id).first()
        if star is None:
            star = CooperationMindStar(operator_user_id=user.id, coop_mind_id=coop_mind_id, coop_mind_name=mind.coop_mind_name)
            star.save()
        return build_response(msg="收藏成功")

    def delete(self, request):
        """
        取消收藏
        """
        post_body = request.POST
        user = request.user
        coop_mind_id = post_body.get('coop_mind_id')
        CooperationMindStar.objects.filter(operator_user_id=user.id, coop_mind_id=coop_mind_id).delete()
        return build_response(msg="取消收藏，操作成功")
