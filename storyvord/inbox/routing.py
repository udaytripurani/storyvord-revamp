from django.urls import re_path
from .consumers.chat_consumer import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<type>user|room)/(?P<id>\d+)/$', ChatConsumer.as_asgi()),
]