# Usamos una imagen base ligera de Python
FROM docker.io/library/python:3.12-slim

# Variables de entorno recomendadas para Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DUCKDB_PATH=/data/sisifo.duckdb \
    REDIS_URL=redis://127.0.0.1:6379/1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Dependencias del sistema mínimas (útiles para compilación o paquetes nativos)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar los requerimientos primero para aprovechar la caché de capas
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Crear un usuario sin privilegios (buena práctica para Podman rootless)
RUN useradd -m -r -u 1000 appuser && \
    mkdir -p /data && \
    chown -R appuser:appuser /app /data && \
    chmod 777 /data

# Copiar el código del proyecto
COPY --chown=appuser:appuser . .

USER appuser

# En un Pod de Podman, todos los contenedores comparten 'localhost'
EXPOSE 8000

# Comando por defecto: aplicar migraciones en DuckDB y levantar servidor Django
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
