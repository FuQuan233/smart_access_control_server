from django.db import models
from django.contrib.auth.models import Group, User
from django.forms import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib import admin


def validate_exact_length(value):
    if len(value) != 16:
        raise ValidationError('Field length must be exactly 16 characters.')
class DoorLock(models.Model):
    name = models.CharField("名称", max_length=200)
    comment = models.CharField("简介", max_length=200)
    key = models.CharField("密钥", max_length=200, validators=[validate_exact_length])
    rolling_code = models.BigIntegerField("滚码", default=0)
    last_seen = models.DateTimeField("上次心跳", default=timezone.datetime.fromisoformat("1970-01-01 00:00:00"))

    class Meta:
        verbose_name = "门禁"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
    
    # 定义一个类方法，用于获取和更新门锁的滚动码
    def get_rolling_code(self):
        # 滚动码自增1
        self.rolling_code += 1
        
        # 防止滚动码溢出
        if self.rolling_code > 9223372036854775807 - 1:
            self.rolling_code = 0
        
        # 保存对象的当前状态
        self.save()
        
        # 返回更新后的滚动码
        return self.rolling_code

    # 在admin面板中显示是否在线的函数
    @admin.display(
        boolean=True,  # 显示为布尔值
        ordering="last_seen",  # 按照last_seen字段排序
        description="是否在线",  # 显示的描述
    )
    def is_online(self):
        # 如果last_seen为None，则不在线
        if self.last_seen is None:
            return False
        
        # 如果当前时间与last_seen的时间差大于13秒，则不在线
        if timezone.now() - self.last_seen > timedelta(seconds=13):
            return False
        
        # 否则在线
        return True

class GroupDoorLock(models.Model):
    comment = models.CharField("描述", max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    doorlock = models.ManyToManyField(DoorLock)
    expireTime = models.DateTimeField("过期时间")

    class Meta:
        verbose_name = "门禁用户组授权"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.comment

class UserDoorLock(models.Model):
    comment = models.CharField("描述", max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doorlock = models.ManyToManyField(DoorLock)
    expireTime = models.DateTimeField("过期时间")

    class Meta:
        verbose_name = "门禁用户授权"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.comment
