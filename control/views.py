from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.http import Http404, JsonResponse
import paho.mqtt.client as mqtt
import json
from Crypto.Cipher import AES
import base64
from .models import *

client = mqtt.Client(1)
client.connect("shanghai.fuquan.moe", 31883)

def get_doorlocks(user: User):
    """
    获取用户的所有门锁
    """
    # 初始化一个空的门锁列表
    doorlock_list = []
    
    # 获取用户的门锁访问权限列表
    user_access_list = UserDoorLock.objects.filter(user=user)
    
    # 遍历用户的门锁访问权限列表
    for one in user_access_list:
        # 如果当前访问权限未过期
        if one.expireTime > timezone.now():
            # 遍历当前访问权限关联的所有门锁
            for one_doorlock in one.doorlock.all():
                # 如果门锁不在门锁列表中，则添加到门锁列表中
                if not doorlock_list.__contains__(one_doorlock):
                    doorlock_list.append(one_doorlock)

    # 获取用户所属群组的门锁访问权限列表
    group_access_list = GroupDoorLock.objects.filter(group__in=user.groups.all())

    # 遍历群组的门锁访问权限列表
    for one in group_access_list:
        # 如果当前访问权限未过期
        if one.expireTime > timezone.now():
            # 遍历当前访问权限关联的所有门锁
            for one_doorlock in one.doorlock.all():
                # 如果门锁不在门锁列表中，则添加到门锁列表中
                if not doorlock_list.__contains__(one_doorlock):
                    doorlock_list.append(one_doorlock)
                    
    # 返回门锁列表
    return doorlock_list


@login_required
def door_locks(request:WSGIRequest):
    """
    门锁列表界面
    """
    doorlock_list = get_doorlocks(request.user)
    return render(request, 'control/doorlocks.html', {'doorlock_list': doorlock_list})

@login_required
def index(request:WSGIRequest):
    return render(request, 'control/index.html')

@login_required
def door_detail(request:WSGIRequest, doorlock_id):
    doorlock_list = get_doorlocks(request.user)
    doorlock = get_object_or_404(DoorLock, pk = doorlock_id)
    if not doorlock_list.__contains__(doorlock):
        raise Http404("No DoorLock matches the given query.")
    return render(request, 'control/door_detail.html',{"doorlock": doorlock})

def pad(text):
    """
    PKCS7 填充函数
    """
    block_size = AES.block_size
    padding_size = block_size - len(text) % block_size
    padding = chr(padding_size) * padding_size
    return text + padding

def unpad(text):
    """
    PKCS7 反填充函数
    """
    padding_size = ord(text[-1])
    return text[:-padding_size]

def encrypt(key, text):
    """
    使用 ECB 模式进行 AES 加密
    """
    cipher = AES.new(key, AES.MODE_ECB)
    padded_text = pad(text)
    encrypted_bytes = cipher.encrypt(padded_text.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def decrypt(key, encrypted_text):
    """
    使用 ECB 模式进行 AES 解密
    """
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_bytes = base64.b64decode(encrypted_text)
    decrypted_bytes = cipher.decrypt(encrypted_bytes)
    return unpad(decrypted_bytes.decode('utf-8'))

def unlock_doorlock(doorlock: DoorLock):
    """
    开启门锁函数，向门锁发送开启信号
    """
    # 初始化一个字典来存储解锁数据
    unlockdata = {}
    
    # 获取门锁的滚动码并添加到解锁数据字典中
    unlockdata["rollingcode"] = doorlock.get_rolling_code()
    
    # 添加解锁动作到解锁数据字典中
    unlockdata["action"] = "open"
    
    # 检查客户端是否已连接，如果未连接则重新连接
    if not client.is_connected():
        client.reconnect()
    
    # 将解锁数据字典转换为JSON字符串
    unlockstr = json.dumps(unlockdata)
    
    # 使用门锁的密钥加密JSON字符串
    ciphertext = encrypt(doorlock.key.encode(), unlockstr)
    
    # 将加密后的字符串发布到以门锁ID命名的频道
    client.publish(str(doorlock.id), ciphertext)

@login_required
def door_unlock(request:WSGIRequest, doorlock_id):
    """
    用户开锁请求
    """
    doorlock_list = get_doorlocks(request.user)
    doorlock = get_object_or_404(DoorLock, pk = doorlock_id)
    if not doorlock_list.__contains__(doorlock):
        raise Http404("No DoorLock matches the given query.")

    if doorlock.is_online():
        try:
            unlock_doorlock(doorlock)

            response_data = {
                'code': 0,
                'message': f"{doorlock.name}开锁成功",
            }
        except:
            response_data = {
                'code': 1,
                'message': f"{doorlock.name}开锁失败",
            }
    else:
        response_data = {
            'code': 1,
            'message': f"{doorlock.name}不在线",
        }
    return JsonResponse(response_data)


