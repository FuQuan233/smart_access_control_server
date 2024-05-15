"""
WSGI config for smart_access_control_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from control.mqtt_handler import start_mqtt_listener

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_access_control_server.settings')

application = get_wsgi_application()

start_mqtt_listener()