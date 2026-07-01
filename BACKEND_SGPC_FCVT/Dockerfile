# Se actualiza a la versión 3.12-slim para cumplir requerimientos de auditoría de EOL
FROM python:3.12-slim

# Evita que Python genere archivos basura (.pyc) y fuerza la salida de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalamos las herramientas del sistema necesarias (incluyendo libmagic para los PDFs)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos el archivo de dependencias e instalamos con gunicorn
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

COPY . /app/

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]