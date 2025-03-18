import os
import environ
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kutok.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from forum import routing as forum_routing
from chat import routing as chat_routing


# Объединяем WebSocket-маршруты
websocket_urlpatterns = forum_routing.websocket_urlpatterns + chat_routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
