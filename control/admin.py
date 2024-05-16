from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from .views import unlock_doorlock
from .models import DoorLock, GroupDoorLock, UserDoorLock
from django.utils import timezone
from datetime import timedelta

admin.site.site_header = "智能门禁系统后台管理"
admin.site.site_title = "后台管理系统"

class DoorLockAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "is_online"]
    search_fields = ["name"]
    actions = ['open_door']
    exclude = ['last_seen']

    def open_door(self, request, queryset):
        # 处理动作的逻辑
        for one in queryset:
            unlock_doorlock(one)
        self.message_user(request, f"{'、'.join(one.name for one in queryset)} 已开启")
    open_door.short_description = "开启所选的 门禁"

admin.site.register(DoorLock, DoorLockAdmin)

class GroupDoorLockAdmin(admin.ModelAdmin):
    list_display = ["comment","group","expireTime"]

admin.site.register(GroupDoorLock,GroupDoorLockAdmin)

class UserDoorLockAdmin(admin.ModelAdmin):
    list_display = ["comment","user","expireTime"]

admin.site.register(UserDoorLock,UserDoorLockAdmin)
