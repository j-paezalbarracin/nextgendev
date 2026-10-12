#!/bin/sh

echo " Aplicando migraciones..."
python manage.py migrate --noinput

echo " Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo " Iniciando Daphne..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} mi_blog.asgi:application