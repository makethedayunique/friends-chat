from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/onetoonechat', consumers.ChatConsumer.as_asgi()),
]