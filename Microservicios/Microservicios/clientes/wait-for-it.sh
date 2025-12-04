#!/usr/bin/env bash
host="$1"
shift

until nc -z "$host" 5432; do
  echo "Esperando a que la base de datos ($host:5432) esté disponible..."
  sleep 1
done

echo "Base de datos disponible. Ejecutando aplicación..."
exec "$@"
