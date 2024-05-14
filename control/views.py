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

def get_doorlocks(user: User):
    doorlock_list = []
    
    user_access_list = UserDoorLock.objects.filter(user=user)
    for one in user_access_list:
        if one.expireTime > timezone.now():
            for one_doorlock in one.doorlock.all():
                if not doorlock_list.__contains__(one_doorlock):
                    doorlock_list.append(one_doorlock)

    group_access_list = GroupDoorLock.objects.filter(group__in=user.groups.all())

    for one in group_access_list:
        if one.expireTime > timezone.now():
            for one_doorlock in one.doorlock.all():
                if not doorlock_list.__contains__(one_doorlock):
                    doorlock_list.append(one_doorlock)
                    
    return doorlock_list

@login_required
def door_locks(request:WSGIRequest):
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

def unlock_doorlock(doorlock:DoorLock):
    client = mqtt.Client(1)
    client.connect("127.0.0.1", 1883)
    unlockdata = {}
    unlockdata["rollingcode"] = doorlock.get_rolling_code()
    unlockdata["action"] = "open"
    unlockstr = json.dumps(unlockdata)
    ciphertext = encrypt(doorlock.key.encode(), unlockstr)
    client.publish(str(doorlock.id), ciphertext)

@login_required
def door_unlock(request:WSGIRequest, doorlock_id):
    doorlock_list = get_doorlocks(request.user)
    doorlock = get_object_or_404(DoorLock, pk = doorlock_id)
    if not doorlock_list.__contains__(doorlock):
        raise Http404("No DoorLock matches the given query.")

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
    return JsonResponse(response_data)


