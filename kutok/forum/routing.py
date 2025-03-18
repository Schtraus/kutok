from django.urls import re_path
from . import consumers  # Импортируем ваш WebSocket-консьюмер

websocket_urlpatterns = [
    # В этот путь будет подключаться WebSocket
    re_path(r'ws/thread/(?P<thread_id>\d+)/$', consumers.CommentConsumer.as_asgi()),
]


