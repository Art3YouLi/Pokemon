from django.db import models


class AbstractModel(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class CooperationMind(AbstractModel):
    """

    """
    coop_mind_name = models.CharField(verbose_name='脑图名称', max_length=128, null=False, blank=False)
    creator_user_id = models.BigIntegerField(verbose_name='创建人ID', null=False, blank=False, default=0)
    client_uuid = models.CharField(verbose_name='客户端ID', max_length=64, null=False, blank=False)
    snapshot_data = models.TextField(verbose_name='脑图数据', null=True, )
    mind_log_id = models.BigIntegerField(verbose_name='data对应的操作日志(cooperation_mind_log)ID', null=True, )
    data_format = models.CharField(verbose_name='数据格式化类型', max_length=32, null=False, blank=False)
    deleted = models.BooleanField(verbose_name='是否标记为软删除', default=False)

    class Meta:
        db_table = 'cooperation_mind'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['creator_user_id'])
        ]
        verbose_name = "脑图表"


# Create your models here.
class CooperationMindLog(AbstractModel):
    """
    操作日志表
    """
    coop_mind = models.ForeignKey(to="CooperationMind", to_field="id", verbose_name="脑图ID", on_delete=models.CASCADE)
    log_uuid = models.CharField(verbose_name='操作UUID', max_length=64, null=False, blank=False)
    log_content = models.CharField(verbose_name='操作内容', max_length=1024, null=False, blank=False)
    operator_user_id = models.BigIntegerField(verbose_name='操作人', null=True)
    operator_ip = models.CharField(verbose_name='操作人IP', null=False, max_length=32)
    client_uuid = models.CharField(verbose_name='客户端ID', max_length=64, null=False, blank=False)

    class Meta:
        db_table = 'cooperation_mind_log'
        ordering = ['id']
        unique_together = (("coop_mind_id", "log_uuid"),)
        indexes = [
            models.Index(fields=['coop_mind_id'], ),
            models.Index(fields=['operator_user_id'], )
        ]
        verbose_name = "操作日志表"


class CooperationMindShare(AbstractModel):
    """
    分享记录表
    """
    coop_mind = models.OneToOneField(to="CooperationMind", to_field="id", verbose_name="脑图ID", on_delete=models.CASCADE)
    coop_mind_name = models.CharField(verbose_name='脑图名称', max_length=128, null=False, blank=False)
    share_uuid = models.CharField(verbose_name='分享uuid', max_length=128, null=False, blank=False)
    share_uuid_hash = models.BigIntegerField(verbose_name='分享uuid_hash', null=False, blank=False)
    share_end_time = models.DateTimeField(verbose_name='分享有效期', null=True)
    operator_user_id = models.BigIntegerField(verbose_name='分享操作人', null=False)

    class Meta:
        db_table = 'cooperation_mind_share'
        indexes = [
            models.Index(fields=['share_uuid_hash'], ),
            models.Index(fields=['operator_user_id'], ),
        ]
        verbose_name = "协作分享表"


class CooperationMindStar(AbstractModel):
    """
    收藏记录表
    """
    operator_user_id = models.BigIntegerField(verbose_name='收藏人', null=False)
    coop_mind = models.ForeignKey(to="CooperationMind", to_field="id", verbose_name="脑图ID", on_delete=models.CASCADE)
    coop_mind_name = models.CharField(verbose_name='脑图名称', max_length=128, null=False, blank=False)

    # star_type = models.SmallIntegerField(verbose_name="收藏类型。1：根据主键收藏；2：根据分享收藏", null=False)

    class Meta:
        db_table = 'cooperation_mind_star'
        indexes = [
            models.Index(fields=['operator_user_id'], ),
        ]
        verbose_name = "协作分享表"
