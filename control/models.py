from django.db import models
from django.contrib.auth.models import Group, User
from django.forms import ValidationError
from django.utils import timezone
from datetime import timedelta

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
    
    def get_rolling_code(self):
        self.rolling_code += 1
        if self.rolling_code > 9223372036854775807 - 1:  #防止溢出
            self.rolling_code = 0
        self.save()
        return self.rolling_code
    
    def is_online(self):
        if self.last_seen == None:
            return False
        if timezone.now() - self.last_seen > timedelta(seconds=20):
            return False
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
