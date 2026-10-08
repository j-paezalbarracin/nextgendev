from django.contrib import admin
from .models import Categoria, Post, Comentario, Perfil, Guardado, Seguir, Notificacion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'slug']
    search_fields = ['nombre']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['titulo','contenido','fecha_publicacion','autor','categoria','imagen']
    list_filter = ['categoria']
    search_fields = ['titulo']

@admin.register(Comentario)
class comentarioAdmin(admin.ModelAdmin):
    list_display = ['post','autor','texto','fecha']
    search_fields = ['post']

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'ubicacion', 'creado']
    search_fields = ['user__username', 'user__email']
    list_filter = ['creado']


@admin.register(Guardado)
class GuardadoAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'creado']
    search_fields = ['user__username', 'post__titulo']
    list_filter = ['creado']


@admin.register(Seguir)
class SeguirAdmin(admin.ModelAdmin):
    list_display = ['seguidor', 'seguido', 'creado']
    search_fields = ['seguidor__username', 'seguido__username']
    list_filter = ['creado']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo', 'actor', 'leida', 'creada']
    list_filter = ['tipo', 'leida', 'creada']
    search_fields = ['usuario__username', 'actor__username']