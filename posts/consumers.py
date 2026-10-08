import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ComentarioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'comentarios_{self.post_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ Conectado al post {self.post_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"🔌 Desconectado del post {self.post_id}")

    async def receive(self, text_data):
        from .models import Post, Comentario
        
        data = json.loads(text_data)
        mensaje = data.get('mensaje')
        usuario = self.scope.get('user')
        
        print(f"📩 Recibido de {usuario}: {mensaje}")
        
        if not usuario.is_authenticated:
            await self.send(text_data=json.dumps({
                'error': 'Debes iniciar sesión'
            }))
            return
        
        try:
            comentario = await self.guardar_comentario(usuario, mensaje)
            # ✅ Obtener avatar de forma segura
            avatar_url = await self.obtener_avatar(usuario)
            print(f"💾 Comentario guardado: ID {comentario.id}")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))
            return
        
        # ✅ ENVIAR A TODOS LOS CONECTADOS (incluyendo al que envió)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'enviar_comentario',
                'mensaje': mensaje,
                'usuario': usuario.username,
                'avatar': avatar_url,
                'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M')
            }
        )

    async def enviar_comentario(self, event):
        # ✅ ENVIAR AL CLIENTE (incluyendo avatar)
        await self.send(text_data=json.dumps({
            'mensaje': event['mensaje'],
            'usuario': event['usuario'],
            'avatar': event.get('avatar'),
            'fecha': event['fecha']
        }))

    @database_sync_to_async
    def guardar_comentario(self, usuario, mensaje):
        from .models import Post, Comentario
        
        post = Post.objects.get(id=self.post_id)
        return Comentario.objects.create(
            post=post,
            autor=usuario,
            texto=mensaje
        )
    
    @database_sync_to_async
    def obtener_avatar(self, usuario):
        """Obtiene la URL del avatar de forma segura (async)"""
        try:
            if usuario.perfil.avatar:
                return usuario.perfil.avatar.url
        except Exception:
            pass
        return None


class NotificacionConsumer(AsyncWebsocketConsumer):
    """
    Consumer que maneja las notificaciones en tiempo real.
    Cada usuario se une a un grupo único: notificaciones_{user_id}
    """
    
    async def connect(self):
        self.user = self.scope['user']
        
        # Si no está autenticado, cerrar conexión
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Grupo único por usuario
        self.group_name = f'notificaciones_{self.user.id}'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f'✅ Notificaciones conectadas para {self.user.username}')
    
    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def nueva_notificacion(self, event):
        """Recibe el evento del grupo y lo envía al cliente"""
        await self.send(text_data=json.dumps({
            'type': 'notificacion',
            'id': event['id'],
            'tipo': event['tipo'],
            'actor': event['actor'],
            'actor_avatar': event['actor_avatar'],
            'post_titulo': event['post_titulo'],
            'post_id': event['post_id'],
            'mensaje': event['mensaje'],
            'creada': event['creada'],
        }))