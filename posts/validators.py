# apps/usuarios/validators.py
import re
from django.core.exceptions import ValidationError

def validate_only_letters(value):
    """Valida que solo contenga letras, espacios, tildes y ñ"""
    if value and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', value):
        raise ValidationError(
            'Solo se permiten letras, espacios, tildes y la letra ñ.'
        )
    return value

def capitalize_name(value):
    """Capitaliza y limpia espacios extra"""
    if value:
        return ' '.join(value.split()).title()
    return value