# Imagen oficial ligera de Redis basada en Alpine
FROM docker.io/library/redis:7.4-alpine

# Copiar el archivo de configuración personalizado
COPY redis.conf /usr/local/etc/redis/redis.conf

# Directorio para persistencia de datos
VOLUME /data
WORKDIR /data

# Puerto por defecto de Redis
EXPOSE 6379

# Iniciar Redis usando nuestra configuración personalizada
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
