"""
WebSocket URL routing for sportscaster
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sportscaster/(?P<channel_id>\w+)/$', consumers.SportscasterConsumer.as_asgi()),
]
