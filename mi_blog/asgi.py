# mi_blog/asgi.py
import os
from django.core.asgi import get_asgi_application

# ✅ PRIMERO: Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_blog.settings')

# ✅ SEGUNDO: Obtener la aplicación Django
django_asgi_app = get_asgi_application()

# ✅ TERCERO: Importar los módulos de Channels (después de configurar Django)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from posts.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})