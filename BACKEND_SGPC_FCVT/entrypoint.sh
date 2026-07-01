#!/bin/bash
# Este script se ejecuta automáticamente al iniciar el contenedor del backend

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Aplicando migraciones a la base de datos..."
python manage.py migrate --noinput

echo "Iniciando servidor Gunicorn para producción..."
# Reemplazamos el servidor de desarrollo por Gunicorn
exec gunicorn BACKEND_SGPC_FCVT.wsgi:application --bind 0.0.0.0:8000 --workers 3