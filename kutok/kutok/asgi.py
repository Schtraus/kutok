import os
import environ
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from forum import routing

# env = environ.Env()
# # Чтение .env файла
# environ.Env.read_env(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# # Выводим переменную окружения для проверки
# print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kutok.settings')

# django.setup()
# django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
