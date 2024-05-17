# mqtt_listener.py
import time
import paho.mqtt.client as mqtt
import logging
from .models import *
from django.utils import timezone

locked = False

def on_message(client, userdata, message):
    """
    当收到门锁的心跳包后的处理
    """
    try:
        print("MQTT received message:", message.topic, message.payload.decode())
        topiclist = message.topic.split("/")
        if topiclist.__len__() > 1 and topiclist[1] == 'heartbeat':
            doorlock_id = int(topiclist[0])
            doorlock = DoorLock.objects.get(pk = doorlock_id)
            doorlock.last_seen = timezone.now()
            doorlock.save()

    except Exception as e:
        print(e)


def on_disconnect(client, userdata, rc):
    """
    MQTT断线重连
    """
    while not client.client.is_connected():
        time.sleep(1)
        print("Disconnected. Trying to reconnect...")
        client.reconnect()

def start_mqtt_listener():
    """
    启动MQTT监听器，监听门锁心跳
    """
    print("Staring MQTT Handler.")
    global locked
    if locked:
        return
    locked = True
    client = mqtt.Client(1)
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    client.reconnect_delay_set(1, 10)
    client.connect("shanghai.fuquan.moe", 31883, 60)
    client.subscribe("+/heartbeat")
    client.loop_start()


