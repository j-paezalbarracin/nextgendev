from django import forms
from .models import Comentario, User, Categoria
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .validators import validate_only_letters, capitalize_name
import re
from django.utils.text import slugify

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control contenido-textarea',
                'rows': 5,
                'placeholder': 'Escribir comentario'
            }),
        }

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PerfilForm(UserChangeForm):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        validators=[validate_only_letters],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        validators=[validate_only_letters],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control bg-light text-muted',  # ✅ Fondo gris y texto gris
                'placeholder': 'Nombre de usuario',
                'readonly': True,  # ✅ Readonly en lugar de disabled
                'style': 'cursor: not-allowed; opacity: 0.85;',  # ✅ Estilo adicional
                'title': 'El nombre de usuario no se puede modificar'  # ✅ Tooltip
                
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar el campo password del formulario de edición
        if 'password' in self.fields:
            del self.fields['password']
    
    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')
        return capitalize_name(data)
    
    def clean_last_name(self):
        data = self.cleaned_data.get('last_name')
        return capitalize_name(data)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado por otro usuario.')
        return email
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 🔥 DESACTIVAR TODOS LOS ERRORES DE DJANGO
        self.fields['old_password'].error_messages = {
            'required': 'La contraseña actual es obligatoria.',
        }
        
        self.fields['new_password1'].error_messages = {
            'required': 'La nueva contraseña es obligatoria.',
        }
        
        self.fields['new_password2'].error_messages = {
            'required': 'La confirmación de la contraseña es obligatoria.',
        }
        
        # Estilos y placeholders
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
            })
        
        self.fields['old_password'].widget.attrs.update({
            'placeholder': 'Escribe tu contraseña actual.'
        })
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Escribe tu nueva contraseña.'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirma tu contraseña nueva.'
        })
    
    def clean_old_password(self):
        """Validación de contraseña actual (ESPAÑOL)"""
        old_password = self.cleaned_data.get('old_password')
        
        if not old_password:
            raise ValidationError("La contraseña actual es obligatoria.")
        
        if not self.user.check_password(old_password):
            raise ValidationError("La contraseña actual es incorrecta.")
        
        return old_password
    
    def clean_new_password1(self):
        """Validación de nueva contraseña (ESPAÑOL)"""
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            raise ValidationError("La nueva contraseña es obligatoria.")
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        if not re.search(r'[0-9]', password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        
        if password.isdigit():
            raise ValidationError("La contraseña no puede ser solo números.")
        
        if self.user and password.lower() == self.user.username.lower():
            raise ValidationError("La contraseña no puede ser igual al nombre de usuario.")
        
        common_passwords = ['password', '12345678', 'qwerty', 'abcdef', 'admin', 'contraseña']
        if password.lower() in common_passwords:
            raise ValidationError("La contraseña es demasiado común. Elige una más segura.")
        
        return password
    
    def clean_new_password2(self):
        """Validación de confirmación de contraseña (ESPAÑOL)"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if not password2:
            raise ValidationError("La confirmación de la contraseña es obligatoria.")
        
        if password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return password2
    
    def clean(self):
        """
        SOBRESCRIBIR clean() PARA EVITAR VALIDACIÓN NATIVA DE DJANGO
        Esto evita que Django muestre el error en inglés por duplicado
        """
        cleaned_data = super().clean()
        
        # 🔥 DESACTIVAR VALIDACIÓN NATIVA DE COINCIDENCIA
        # Ya validamos en clean_new_password2, así que no hacemos nada aquí
        return cleaned_data

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'slug']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tecnología, Python, Django...'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Se genera automaticamente...',
                'readonly': True,  # 👈 Solo lectura, se genera solo
            }),
        }
        labels = {
            'nombre': 'Nombre de la categoría',
            'slug': 'Slug (URL amigable)',
        }
        help_texts = {
            'nombre': 'Máximo 100 caracteres.',
            'slug': 'Se genera automáticamente desde el nombre.',
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Categoria.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe una categoría con este nombre.')
        return nombre

    def clean_slug(self):
        # Si el slug está vacío, se genera desde el nombre
        slug = self.cleaned_data.get('slug')
        nombre = self.cleaned_data.get('nombre')
        
        if not slug and nombre:
            slug = slugify(nombre)
        
        # Verificar que el slug sea único
        if slug and Categoria.objects.filter(slug=slug).exists():
            raise forms.ValidationError('Ya existe una categoría con este slug.')
        
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Si el slug está vacío, generarlo desde el nombre
        if not instance.slug:
            instance.slug = slugify(instance.nombre)
        if commit:
            instance.save()
        return instance
    
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario',
            'id': 'username'
        }),
        label='Usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'id': 'password'
        }),
        label='Contraseña'
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('El usuario es obligatorio')
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('La contraseña es obligatoria')
        return password