from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Categoria, User, Like, Notificacion, Seguir, Guardado
from .forms import ComentarioForm, RegistroForm, PerfilForm, CustomPasswordChangeForm, CategoriaForm, LoginForm 
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Vistas basadas en funciones
def inicio(request):
    posts_list = Post.objects.select_related('autor', 'categoria') \
                        .prefetch_related('comentarios') \
                        .order_by('-fecha_publicacion')
    
    # ==========================================
    # PAGINACIÓN: 5 posts por página
    # ==========================================
    paginator = Paginator(posts_list, 5)  # 5 posts por página
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categorias = Categoria.objects.all()
    
    # ==========================================
    # AGREGAR INFORMACIÓN DE LIKES A CADA POST
    # ==========================================
    for post in posts:
        post.likes_count = post.likes.count()
        post.user_has_liked = False
        post.user_has_saved = False
        if request.user.is_authenticated:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
            post.user_has_saved = post.guardados.filter(user=request.user).exists()
    
    return render(request, 'posts/inicio.html', {
        'posts': posts,
        'categorias': categorias,
        'page_obj': posts,  # Para saber si hay más páginas
    })

def api_posts(request):
    """Devuelve posts en JSON para scroll infinito (sin duplicados)"""
    
    # ==========================================
    # PARÁMETROS
    # ==========================================
    last_id = request.GET.get('last_id')
    categoria_id = request.GET.get('categoria_id')
    guardados = request.GET.get('guardados')
    perfil_username = request.GET.get('perfil_username')
    feed = request.GET.get('feed')
    posts_per_page = 5
    
    # ==========================================
    # CONSULTA BASE
    # ==========================================
    queryset = Post.objects.select_related('autor', 'categoria') \
                        .prefetch_related('comentarios') \
                        .order_by('-fecha_publicacion', '-id')

    # ==========================================
    # FILTRO POR GUARDADOS (si viene)
    # ==========================================
    if guardados == 'true':
        if request.user.is_authenticated:
            # Solo los posts guardados por el usuario
            guardados_ids = Guardado.objects.filter(user=request.user).values_list('post_id', flat=True)
            queryset = queryset.filter(id__in=guardados_ids)
        else:
            return JsonResponse({'posts': [], 'has_next': False, 'next_cursor': None})

    # ==========================================
    # FILTRO POR PERFIL (si viene)
    # ==========================================
    if perfil_username:
        queryset = queryset.filter(autor__username=perfil_username)

    # ==========================================
    # FILTRO POR CATEGORÍA (si viene)
    # ==========================================
    if categoria_id:
        try:
            categoria_id = int(categoria_id)
            queryset = queryset.filter(categoria_id=categoria_id)
        except ValueError:
            return JsonResponse({'posts': [], 'has_next': False, 'next_cursor': None})

    # ==========================================
    # FILTRO POR CURSOR (last_id)
    # ==========================================
    if last_id:
        try:
            last_id = int(last_id)
            queryset = queryset.filter(id__lt=last_id)
        except ValueError:
            return JsonResponse({'posts': [], 'has_next': False, 'next_cursor': None})

    # ==========================================
    # FILTRO POR FEED PERSONALIZADO 
    # ==========================================
    if feed == 'true':
        if request.user.is_authenticated:
            siguiendo_ids = Seguir.objects.filter(
                seguidor=request.user
            ).values_list('seguido_id', flat=True)
            queryset = queryset.filter(autor_id__in=siguiendo_ids)
        else:
            return JsonResponse({'posts': [], 'has_next': False, 'next_cursor': None})
    
    # ==========================================
    # TRAEMOS UNO MÁS PARA SABER SI HAY MÁS
    # ==========================================
    posts = list(queryset[:posts_per_page + 1])
    
    has_next = len(posts) > posts_per_page
    if has_next:
        posts = posts[:-1]
    
    next_cursor = posts[-1].id if posts else None
    
    # ==========================================
    # SERIALIZAR
    # ==========================================
    data = []
    for post in posts:
        likes_count = post.likes.count()
        user_has_liked = False
        if request.user.is_authenticated:
            user_has_liked = post.likes.filter(user=request.user).exists()
        
        data.append({
            'id': post.id,
            'titulo': post.titulo,
            'contenido': post.contenido[:250] + '...' if len(post.contenido) > 250 else post.contenido,
            'autor': post.autor.username,
            'fecha': post.fecha_publicacion.strftime('%d/%m/%Y'),
            'categoria': post.categoria.nombre if post.categoria else None,
            'imagen': post.imagen.url if post.imagen else None,
            'likes_count': likes_count,
            'user_has_liked': user_has_liked,
            'comentarios_count': post.comentarios.count(),
            'user_has_saved': post.guardados.filter(user=request.user).exists() if request.user.is_authenticated else False,
        })
    
    return JsonResponse({
        'posts': data,
        'has_next': has_next,
        'next_cursor': next_cursor,
        'current_count': len(data),
    })

def api_search(request):
    """Busca posts por título y devuelve resultados en JSON"""
    query = request.GET.get('q', '').strip()
    
    # Si no hay query o es muy corto, devolver vacío
    if not query or len(query) < 2:
        return JsonResponse({
            'results': [],
            'query': query,
            'count': 0
        })
    
    # Buscar posts por título (insensible a mayúsculas)
    posts = Post.objects.filter(
        titulo__icontains=query
    ).order_by('-fecha_publicacion')[:10]
    
    # Serializar (solo id y título)
    data = [{'id': p.id, 'titulo': p.titulo} for p in posts]
    
    return JsonResponse({
        'results': data,
        'query': query,
        'count': len(data)
    })

def Verpost_categoria(request, pk):
    # 1. Obtener la categoría específica
    categoria_actual = get_object_or_404(Categoria, id=pk)
    
    # 2. Obtener los posts de esa categoría
    posts_list = Post.objects.filter(categoria_id=pk).order_by('-fecha_publicacion')
    
    # ==========================================
    # PAGINACIÓN: 5 posts por página
    # ==========================================
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # ==========================================
    # AGREGAR INFORMACIÓN DE LIKES A CADA POST
    # ==========================================
    for post in posts:
        post.likes_count = post.likes.count()
        post.user_has_liked = False
        post.user_has_saved = False
        if request.user.is_authenticated:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
            post.user_has_saved = post.guardados.filter(user=request.user).exists()
    
    # 3. Obtener TODAS las categorías
    categorias = Categoria.objects.all()
    
    return render(request, 'categoria/verpost_categoria.html', {
        'posts': posts,
        'categoria_actual': categoria_actual,
        'categorias': categorias,
        'page_obj': posts,
        'categoria_id': pk,  # ← Para el JavaScript
    })

def detalle_post(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('autor', 'categoria'),
        pk=pk
    )
    comentarios = post.comentarios.all().order_by('-fecha')
    categorias = Categoria.objects.all()
    
    # ==========================================
    # ASIGNAR AL OBJETO POST (como en inicio)
    # ==========================================
    post.likes_count = post.likes.count()
    post.user_has_liked = False
    post.user_has_saved = False
    if request.user.is_authenticated:
        post.user_has_liked = post.likes.filter(user=request.user).exists()
        post.user_has_saved = post.guardados.filter(user=request.user).exists()
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.post = post
            comentario.save()
            return redirect('detalle_post', pk=post.pk)
    else:
        form = ComentarioForm()
    
    return render(request, 'posts/detalle.html', {
        'post': post,
        'comentarios': comentarios,
        'form': form,
        'categorias': categorias,
        # ❌ NO necesitas pasar user_has_liked aparte
    })

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Inicia sesión automáticamente
            messages.success(request, '¡Registro exitoso! Bienvenido a Mi Blog.')
            return redirect('inicio')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = RegistroForm()
    categorias = Categoria.objects.all()
    return render(request, 'registration/registro.html', {
        'form': form,
        'categorias': categorias
        })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
                return render(request, 'registration/login.html', {'form': form})
        else:
            messages.error(request, 'Por favor, completa todos los campos correctamente')
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = LoginForm()
        categorias = Categoria.objects.all()
        return render(request, 'registration/login.html', {
        'form': form,
        'categorias': categorias
        })

def perfil_publico(request, username):
    """Muestra el perfil público de un usuario"""
    usuario = get_object_or_404(User, username=username)
    perfil = usuario.perfil
    
    # Posts del usuario (paginados)
    posts_list = Post.objects.filter(autor=usuario).order_by('-fecha_publicacion')
    
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    categorias = Categoria.objects.all()
    # Calcular likes para cada post
    for post in posts:
        post.likes_count = post.likes.count()
        post.user_has_liked = False
        if request.user.is_authenticated:
            post.user_has_liked = post.likes.filter(user=request.user).exists()
            post.user_has_saved = post.guardados.filter(user=request.user).exists()
    
    # ¿Es el perfil del usuario logueado?
    es_mi_perfil = request.user.is_authenticated and request.user == usuario
    
    # ¿Ya lo sigue?
    ya_sigue = False
    if request.user.is_authenticated and not es_mi_perfil:
        ya_sigue = Seguir.objects.filter(seguidor=request.user, seguido=usuario).exists()
        
    
    context = {
        'usuario': usuario,
        'perfil': perfil,
        'posts': posts,
        'es_mi_perfil': es_mi_perfil,
        'ya_sigue': ya_sigue,
        'categorias': categorias, 
    }
    
    return render(request, 'posts/perfil_publico.html', context)

@login_required
def editar_perfil(request):
    """Editar el perfil del usuario actual"""
    perfil = request.user.perfil
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        # Datos del User
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        # Datos del Perfil
        perfil.bio = request.POST.get('bio', '').strip()
        perfil.ubicacion = request.POST.get('ubicacion', '').strip()
        perfil.sitio_web = request.POST.get('sitio_web', '').strip()
        
        # Avatar (solo si se subió uno nuevo)
        if request.FILES.get('avatar'):
            perfil.avatar = request.FILES.get('avatar')
        
        # Fecha de nacimiento
        fecha_nac = request.POST.get('fecha_nacimiento', '').strip()
        if fecha_nac:
            perfil.fecha_nacimiento = fecha_nac
        else:
            perfil.fecha_nacimiento = None
        
        perfil.save()
        
        messages.success(request, '¡Perfil actualizado correctamente!')
        return redirect('perfil_publico', username=request.user.username)
    
    context = {
        'perfil': perfil,
        'categorias': categorias,
    }
    
    return render(request, 'registration/editar_perfil.html', context)

@login_required
@require_POST
def toggle_guardado(request, post_id):
    """
    Guarda o quita un post de los guardados del usuario.
    Devuelve JSON con el estado actualizado.
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    guardado = Guardado.objects.filter(user=user, post=post).first()
    
    if guardado:
        guardado.delete()
        saved = False
        mensaje = 'Post eliminado de guardados'
    else:
        Guardado.objects.create(user=user, post=post)
        saved = True
        mensaje = 'Post guardado'
    
    return JsonResponse({
        'success': True,
        'saved': saved,
        'mensaje': mensaje
    })

@login_required
def mis_guardados(request):
    """Muestra los posts guardados del usuario (con paginación)"""
    guardados = Guardado.objects.filter(user=request.user) \
                                .select_related('post', 'post__autor', 'post__categoria') \
                                .order_by('-creado')
    
    posts_list = [g.post for g in guardados]
    
    # ==========================================
    # PAGINACIÓN: 5 posts por página
    # ==========================================
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # ==========================================
    # AGREGAR INFO DE LIKES Y GUARDADOS
    # ==========================================
    for post in posts:
        post.likes_count = post.likes.count()
        post.user_has_liked = post.likes.filter(user=request.user).exists()
        post.user_has_saved = True  # Todos están guardados
    
    categorias = Categoria.objects.all()
    
    return render(request, 'posts/mis_guardados.html', {
        'posts': posts,
        'categorias': categorias,
        'page_obj': posts,
    })

@login_required
def cambiar_contrasena(request):

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Contraseña actualizada exitosamente!')
            return redirect('perfil', pk=user.id)
    
    else:
        form = CustomPasswordChangeForm(user=request.user)
    categorias = Categoria.objects.all()

    return render(request, 'registration/cambiar_contrasena.html', {
        'form': form,
        'categorias': categorias
        })

@login_required
def crear_categoria(request):
    # Solo usuarios staff pueden crear categorías
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para crear categorías.')
        return redirect('inicio')
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f' Categoría "{categoria.nombre}" creada exitosamente.')
            return redirect('inicio')
        else:
            messages.error(request, ' Error al crear la categoría. Corrige los errores.')
    else:
        form = CategoriaForm()
    
    categorias = Categoria.objects.all()
    
    return render(request, 'categoria/crear_categoria.html', {
        'form': form,
        'categorias': categorias,
    })

@login_required
@require_POST
def toggle_like(request, post_id):
    """
    Vista que maneja dar/quitar like a un post.
    Recibe el ID del post por POST y devuelve JSON con el estado actualizado.
    """
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    
    # Buscar si el usuario ya dio like a este post
    like = Like.objects.filter(post=post, user=user).first()
    
    if like:
        # Si existe, lo elimina (quitar like)
        like.delete()
        liked = False
        mensaje = 'Like eliminado'
    else:
        # Si no existe, lo crea (dar like)
        Like.objects.create(post=post, user=user)
        liked = True
        mensaje = 'Like agregado'
    
    # Contar likes actualizados
    likes_count = post.likes.count()
    
    # Devolver respuesta JSON
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': likes_count,
        'mensaje': mensaje
    })

@login_required
@require_POST
def toggle_seguir(request, user_id):
    """
    Sigue o deja de seguir a un usuario.
    Devuelve JSON con el estado actualizado.
    """
    usuario_a_seguir = get_object_or_404(User, id=user_id)
    
    # No puedes seguirte a ti mismo
    if request.user == usuario_a_seguir:
        return JsonResponse({
            'success': False,
            'error': 'No puedes seguirte a ti mismo'
        }, status=400)
    
    seguir = Seguir.objects.filter(
        seguidor=request.user, 
        seguido=usuario_a_seguir
    ).first()
    
    if seguir:
        seguir.delete()
        siguiendo = False
        mensaje = f'Has dejado de seguir a {usuario_a_seguir.username}'
    else:
        Seguir.objects.create(
            seguidor=request.user, 
            seguido=usuario_a_seguir
        )
        siguiendo = True
        mensaje = f'Ahora sigues a {usuario_a_seguir.username}'
    
    # Contar seguidores actualizados
    total_seguidores = usuario_a_seguir.seguidores.count()
    
    return JsonResponse({
        'success': True,
        'siguiendo': siguiendo,
        'total_seguidores': total_seguidores,
        'mensaje': mensaje
    })

def seguidores(request, username):
    """Muestra los seguidores de un usuario"""
    usuario = get_object_or_404(User, username=username)
    
    # Usuarios que siguen a este usuario
    seguidores_list = User.objects.filter(
        siguiendo__seguido=usuario
    ).select_related('perfil')
    
    # Calcular si el usuario actual sigue a cada uno
    for u in seguidores_list:
        u.ya_sigue = False
        if request.user.is_authenticated and request.user != u:
            u.ya_sigue = Seguir.objects.filter(
                seguidor=request.user, 
                seguido=u
            ).exists()
    
    categorias = Categoria.objects.all()
    
    return render(request, 'posts/seguidores.html', {
        'usuario': usuario,
        'usuarios': seguidores_list,
        'tipo': 'seguidores',
        'categorias': categorias,
    })

def siguiendo(request, username):
    """Muestra los usuarios que sigue un usuario"""
    usuario = get_object_or_404(User, username=username)
    
    # Usuarios a los que sigue este usuario
    siguiendo_list = User.objects.filter(
        seguidores__seguidor=usuario
    ).select_related('perfil')
    
    # Calcular si el usuario actual sigue a cada uno
    for u in siguiendo_list:
        u.ya_sigue = False
        if request.user.is_authenticated and request.user != u:
            u.ya_sigue = Seguir.objects.filter(
                seguidor=request.user, 
                seguido=u
            ).exists()
    
    categorias = Categoria.objects.all()
    
    return render(request, 'posts/seguidores.html', {
        'usuario': usuario,
        'usuarios': siguiendo_list,
        'tipo': 'siguiendo',
        'categorias': categorias,
    })

@login_required
def notificaciones(request):
    """Página completa de notificaciones"""
    notifs = Notificacion.objects.filter(usuario=request.user) \
                                .select_related('actor', 'post', 'comentario', 'actor__perfil') \
                                .order_by('-creada')
    
    # Marcar todas como leídas al entrar
    notifs.filter(leida=False).update(leida=True)
    
    categorias = Categoria.objects.all()
    
    return render(request, 'posts/notificaciones.html', {
        'notificaciones': notifs,
        'categorias': categorias,
    })


@login_required
def api_notificaciones(request):
    """API para el dropdown (últimas 10)"""
    notifs = Notificacion.objects.filter(usuario=request.user) \
                                .select_related('actor', 'post', 'actor__perfil') \
                                .order_by('-creada')[:10]
    
    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'tipo': n.tipo,
            'actor': n.actor.username,
            'actor_avatar': n.actor.perfil.avatar.url if n.actor.perfil.avatar else None,
            'post_titulo': n.post.titulo if n.post else None,
            'post_id': n.post.id if n.post else None,
            'leida': n.leida,
            'creada': n.creada.strftime('%d/%m/%Y %H:%M'),
        })
    
    total_no_leidas = Notificacion.objects.filter(
        usuario=request.user, leida=False
    ).count()
    
    return JsonResponse({
        'notificaciones': data,
        'total_no_leidas': total_no_leidas,
    })

@login_required
@require_POST
def marcar_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
    return JsonResponse({'success': True})

@login_required
@require_POST
def marcar_notificacion_leida(request, notif_id):
    """Marca UNA notificación como leída"""
    try:
        notif = Notificacion.objects.get(id=notif_id, usuario=request.user)
        notif.leida = True
        notif.save()
        
        # Contar las que quedan sin leer
        total_no_leidas = Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'total_no_leidas': total_no_leidas
        })
    except Notificacion.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No encontrada'}, status=404)

@login_required
def feed_personalizado(request):
    """Muestra solo los posts de usuarios que sigues"""
    
    # Obtener IDs de usuarios que sigo
    siguiendo_ids = Seguir.objects.filter(
        seguidor=request.user
    ).values_list('seguido_id', flat=True)
    
    # Posts de esos usuarios (paginados)
    posts_list = Post.objects.filter(
        autor_id__in=siguiendo_ids
    ).select_related('autor', 'categoria') \
    .prefetch_related('comentarios') \
    .order_by('-fecha_publicacion')
    
    paginator = Paginator(posts_list, 5)
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # Agregar likes/guardados a cada post
    for post in posts:
        post.likes_count = post.likes.count()
        post.user_has_liked = post.likes.filter(user=request.user).exists()
        post.user_has_saved = post.guardados.filter(user=request.user).exists()
    
    categorias = Categoria.objects.all()
    
    # ¿Sigue a alguien?
    sigue_a_alguien = siguiendo_ids.exists()
    
    return render(request, 'posts/feed.html', {
        'posts': posts,
        'categorias': categorias,
        'page_obj': posts,
        'sigue_a_alguien': sigue_a_alguien,
    })

# Vistas basadas en clases (para crear/editar/eliminar)
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['titulo', 'contenido', 'categoria', 'imagen']
    template_name = 'posts/crear_post.html'
    success_url = reverse_lazy('inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()  # 👈 ESTO ES LO QUE FALTA
        return context
    # Agregar estilos directamente
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Estilo para todos los campos
        for field in form.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
        
        # Estilo específico para un campo en particular
        form.fields['contenido'].widget.attrs.update({
            'class': 'form-control contenido-textarea',
            'rows': 5,
            'placeholder': 'Escribe tu contenido aquí...'
        })
        
        return form

    def form_valid(self, form):
        # le agrego el autor, que es el usuario 
        form.instance.autor = self.request.user
        # Capitalizar el título ANTES de guardar
        form.instance.titulo = form.instance.titulo.capitalize()
        form.instance.contenido = form.instance.contenido.capitalize()
        # Agregar el mensaje de éxito
        messages.success(self.request, '¡Nuevo post agregado correctamente!')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['titulo', 'contenido', 'categoria', 'imagen']
    template_name = 'posts/editar_post.html'
    success_url = reverse_lazy('inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()  # 👈 ESTO ES LO QUE FALTA
        return context
    # Agregar estilos directamente
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Estilo para todos los campos
        for field in form.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
        # Estilo específico para un campo en particular
        form.fields['contenido'].widget.attrs.update({
            'class': 'form-control contenido-textarea',
            'rows': 5,
            'placeholder': 'Escribe tu contenido aquí...'
        })
        return form

    def get_queryset(self):
        return Post.objects.filter(autor=self.request.user)

    def form_valid(self, form):
        # Guardar el formulario
        response = super().form_valid(form)
        # Agregar el mensaje de éxito
        form.instance.titulo = form.instance.titulo.capitalize()
        form.instance.contenido = form.instance.contenido.capitalize()
        messages.success(self.request, '¡Post actualizado correctamente!')
        return response

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/eliminar_post.html'
    success_url = reverse_lazy('inicio')

    def get_queryset(self):
        return Post.objects.filter(autor=self.request.user)

    def form_valid(self, form):
        # Guardar el formulario
        response = super().form_valid(form)
        # Agregar el mensaje de éxito
        messages.success(self.request, '¡Post eliminado correctamente!')
        return response

class PerfilView(LoginRequiredMixin, UpdateView):
    """Vista para editar perfil de usuario"""
    model = User
    form_class = PerfilForm
    template_name = 'registration/perfil.html'
    success_url = reverse_lazy('inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()  # 👈 ESTO ES LO QUE FALTA
        return context

    def get_queryset(self):
        # Solo permitir que el usuario edite su propio perfil
        return User.objects.filter(id=self.request.user.id)

    def form_valid(self, form):
        # Guardar el formulario
        response = super().form_valid(form)
        # Agregar el mensaje de éxito
        messages.success(self.request, '¡Usuario actualizado correctamente!')
        return response

