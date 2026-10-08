from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import PostCreateView, PostUpdateView, PostDeleteView, PerfilView, crear_categoria 

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('api/posts/', views.api_posts, name='api_posts'),
    path('api/search/', views.api_search, name='api_search'),
    path('post/<int:pk>/', views.detalle_post, name='detalle_post'),
    path('post/nuevo/', PostCreateView.as_view(), name='crear_post'),
    path('post/<int:pk>/editar/', PostUpdateView.as_view(), name='editar_post'),
    path('post/<int:pk>/eliminar/', PostDeleteView.as_view(), name='eliminar_post'),
    #path('perfil/<int:pk>/', PerfilView.as_view(), name='perfil'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('verpost_categoria/<int:pk>/', views.Verpost_categoria, name='verpost_categoria'),
    path('categoria/crear/', crear_categoria, name='crear_categoria'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    # Seguir/dejar de seguir
    path('seguir/<int:user_id>/', views.toggle_seguir, name='toggle_seguir'),
    # Seguidores y siguiendo
    path('perfil/<str:username>/seguidores/', views.seguidores, name='seguidores'),
    path('perfil/<str:username>/siguiendo/', views.siguiendo, name='siguiendo'),
    path('perfil/<str:username>/', views.perfil_publico, name='perfil_publico'),
    path('guardar/<int:post_id>/', views.toggle_guardado, name='toggle_guardado'),
    path('guardados/', views.mis_guardados, name='mis_guardados'),
    # Notificaciones
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('api/notificaciones/', views.api_notificaciones, name='api_notificaciones'),
    path('notificaciones/leer/', views.marcar_leidas, name='marcar_leidas'),
    path('notificaciones/<int:notif_id>/leer/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    # Feed personalizado
    path('feed/', views.feed_personalizado, name='feed_personalizado'),
]