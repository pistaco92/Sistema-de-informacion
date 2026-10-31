# Imagen ligera basada en Python para ejecutar y gestionar DuckDB en el Pod
FROM docker.io/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DUCKDB_PATH=/data/sisifo.duckdb

WORKDIR /duckdb_service

# Instalar duckdb y utilidades mínimas
RUN pip install --upgrade pip && \
    pip install "duckdb>=1.1"

# Crear usuario sin privilegios (mismo UID 1000 que el contenedor de Django para compartir volumen)
RUN useradd -m -r -u 1000 appuser && \
    mkdir -p /data && \
    chown -R appuser:appuser /data /duckdb_service

COPY --chown=appuser:appuser init.sql /duckdb_service/init.sql
COPY --chown=appuser:appuser entrypoint.sh /duckdb_service/entrypoint.sh
RUN chmod +x /duckdb_service/entrypoint.sh

VOLUME /data
USER appuser

ENTRYPOINT ["/duckdb_service/entrypoint.sh"]
