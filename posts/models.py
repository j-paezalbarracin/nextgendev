from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.nombre

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    imagen = models.ImageField(upload_to='posts/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.titulo:
            self.titulo = self.titulo.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comentario de {self.autor} en {self.post}"

class Like(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Un usuario solo puede dar like una vez por post
        unique_together = ['post', 'user']
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.user.username} like {self.post.titulo[:20]}"

# ==========================================
# MODELO: PERFIL
# ==========================================
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biografía')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Avatar')
    sitio_web = models.URLField(blank=True, verbose_name='Sitio web')
    ubicacion = models.CharField(max_length=100, blank=True, verbose_name='Ubicación')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de nacimiento')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def total_posts(self):
        return self.user.post_set.count()
    
    @property
    def total_seguidores(self):
        return self.user.seguidores.count()
    
    @property
    def total_siguiendo(self):
        return self.user.siguiendo.count()

# ==========================================
# MODELO: GUARDADO (Marcadores/Favoritos)
# ==========================================
class Guardado(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guardados')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='guardados')
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-creado']
        verbose_name = 'Guardado'
        verbose_name_plural = 'Guardados'
    
    def __str__(self):
        return f"{self.user.username} guardó {self.post.titulo}"

# ==========================================
# MODELO: SEGUIR (Seguidores)
# ==========================================
class Seguir(models.Model):
    seguidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siguiendo')
    seguido = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seguidores')
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['seguidor', 'seguido']
        ordering = ['-creado']
        verbose_name = 'Seguir'
        verbose_name_plural = 'Seguir'
    
    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"

# ==========================================
# MODELO: NOTIFICACIÓN
# ==========================================
class Notificacion(models.Model):
    TIPOS = [
        ('like', 'Like'),
        ('comentario', 'Comentario'),
        ('seguir', 'Seguir'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='acciones')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, null=True, blank=True)
    leida = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-creada']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"{self.actor.username} {self.tipo} a {self.usuario.username}"


