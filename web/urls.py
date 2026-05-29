#前台管理子路由
from django.urls import path

from web.views import index

urlpatterns = [
    path('', index.index, name="web_index"),
]












