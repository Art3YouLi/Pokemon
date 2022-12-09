from django.urls import re_path

from . import consumers
from . import consumers_qr

websocket_urlpatterns = [
    re_path(r'ws/jsmind/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/qr/$', consumers_qr.QrConsumer.as_asgi()),
]
