from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from .models import DoorLock, GroupDoorLock, UserDoorLock

admin.site.site_header = "智能门禁系统后台管理"
admin.site.site_title = "后台管理系统"

class DoorLockAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

admin.site.register(DoorLock, DoorLockAdmin)

class GroupDoorLockAdmin(admin.ModelAdmin):
    list_display = ["comment","group","expireTime"]

admin.site.register(GroupDoorLock,GroupDoorLockAdmin)

class UserDoorLockAdmin(admin.ModelAdmin):
    list_display = ["comment","user","expireTime"]

admin.site.register(UserDoorLock,UserDoorLockAdmin)
