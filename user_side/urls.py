# myapp/urls.py

from django.urls import path
from .views import user_login  # 导入处理登录的视图函数

urlpatterns = [
    path('login/', user_login, name='login'),  # 将 '/login/' 映射到 user_login 视图
    # 其他 URL 映射...
]