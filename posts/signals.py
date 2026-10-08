from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Like, Comentario, Seguir, Notificacion, Perfil, Categoria, Post, Guardado, User


# ==========================================
# FUNCIÓN AUXILIAR: ENVIAR NOTIFICACIÓN POR WEBSOCKET
# ==========================================
def enviar_notificacion_ws(notif):
    """Envía una notificación al grupo WebSocket del usuario"""
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'notificaciones_{notif.usuario.id}',
        {
            'type': 'nueva_notificacion',
            'id': notif.id,
            'tipo': notif.tipo,
            'actor': notif.actor.username,
            'actor_avatar': notif.actor.perfil.avatar.url if notif.actor.perfil.avatar else None,
            'post_titulo': notif.post.titulo if notif.post else None,
            'post_id': notif.post.id if notif.post else None,
            'mensaje': obtener_mensaje(notif),
            'creada': notif.creada.strftime('%d/%m/%Y %H:%M'),
        }
    )


def obtener_mensaje(notif):
    """Devuelve el texto de la notificación según su tipo"""
    if notif.tipo == 'like':
        return f'{notif.actor.username} le dio like a tu post'
    elif notif.tipo == 'comentario':
        return f'{notif.actor.username} comentó en tu post'
    elif notif.tipo == 'seguir':
        return f'{notif.actor.username} empezó a seguirte'
    return 'Nueva notificación'


# ==========================================
# SIGNAL: LIKE
# ==========================================
@receiver(post_save, sender=Like)
def notificar_like(sender, instance, created, **kwargs):
    if created and instance.user != instance.post.autor:
        notif = Notificacion.objects.create(
            usuario=instance.post.autor,
            tipo='like',
            actor=instance.user,
            post=instance.post,
        )
        enviar_notificacion_ws(notif)


# ==========================================
# SIGNAL: COMENTARIO
# ==========================================
@receiver(post_save, sender=Comentario)
def notificar_comentario(sender, instance, created, **kwargs):
    if created and instance.autor != instance.post.autor:
        notif = Notificacion.objects.create(
            usuario=instance.post.autor,
            tipo='comentario',
            actor=instance.autor,
            post=instance.post,
            comentario=instance,
        )
        enviar_notificacion_ws(notif)


# ==========================================
# SIGNAL: SEGUIR
# ==========================================
@receiver(post_save, sender=Seguir)
def notificar_seguir(sender, instance, created, **kwargs):
    if created:
        notif = Notificacion.objects.create(
            usuario=instance.seguido,
            tipo='seguir',
            actor=instance.seguidor,
        )
        enviar_notificacion_ws(notif)

# ==========================================
# SIGNALS: Crear perfil automáticamente
# ==========================================
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()