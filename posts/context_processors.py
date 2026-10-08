from .models import Post, User, Comentario, Categoria
from django.db.models import Count

def sidebar_data(request):
    """Datos para el sidebar derecho (disponible en todas las vistas)"""
    
    # Posts más populares (por likes)
    posts_populares = Post.objects.annotate(
        num_likes=Count('likes')
    ).order_by('-num_likes')[:5]
    
    # Posts recientes
    posts_recientes = Post.objects.order_by('-fecha_publicacion')[:5]
    
    # Autores destacados (con más posts)
    autores_destacados = User.objects.annotate(
        num_posts=Count('post')
    ).filter(num_posts__gt=0).order_by('-num_posts')[:3]
    
    # Estadísticas
    total_posts = Post.objects.count()
    total_usuarios = User.objects.count()
    total_comentarios = Comentario.objects.count()
    
    return {
        'posts_populares': posts_populares,
        'posts_recientes': posts_recientes,
        'autores_destacados': autores_destacados,
        'total_posts': total_posts,
        'total_usuarios': total_usuarios,
        'total_comentarios': total_comentarios,
    }