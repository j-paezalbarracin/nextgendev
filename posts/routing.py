# posts/routing.py
from django.urls import re_path
from . import consumers  # ← Importa consumers de la misma app

websocket_urlpatterns = [
    re_path(r'ws/comentarios/(?P<post_id>\d+)/$', consumers.ComentarioConsumer.as_asgi()),
    re_path(r'ws/notificaciones/$', consumers.NotificacionConsumer.as_asgi()),
]