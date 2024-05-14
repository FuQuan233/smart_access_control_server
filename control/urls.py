# myapp/urls.py

from django.urls import path
from . import views

app_name = 'control'
urlpatterns = [
    path('doorlocks/', views.door_locks, name='doorlocks'),
    path('', views.index, name='index'),
    path("doorlocks/<int:doorlock_id>/", views.door_detail, name="detail"),
    path("doorlocks/<int:doorlock_id>/unlock", views.door_unlock, name="unlock"),
]