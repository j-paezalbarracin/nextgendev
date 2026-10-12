# ============================================
# Dockerfile para NextGenDev
# ============================================

# Imagen base
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "mi_blog.asgi:application"]