# mqtt_listener.py
import paho.mqtt.client as mqtt
import logging
from .models import *
from django.utils import timezone

locked = False

def on_message(client, userdata, message):
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


def start_mqtt_listener():
    print("Staring MQTT Handler.")
    global locked
    if locked:
        return
    locked = True
    client = mqtt.Client(1)
    client.on_message = on_message
    client.reconnect_delay_set(1, 10)
    client.connect("10.0.0.183", 1883, 60)
    client.subscribe("+/heartbeat")
    client.loop_start()


