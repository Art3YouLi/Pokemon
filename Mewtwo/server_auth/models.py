from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class MindUser(AbstractUser):
    # 继承了AbstractUser拥有的所有字段
    # 自定义我们需要的字段
    wx_openid = models.CharField(verbose_name='微信openid', max_length=64, null=True, blank=True)
    wx_nick_name = models.CharField(verbose_name='微信名称', max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'mind_user'
        ordering = ['-id']
        verbose_name = "脑图用户表"
