#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  sleep 1
done

python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput

set -- uvicorn config.asgi:application --host 0.0.0.0 --port "${UVICORN_PORT:-8000}"

if [ "${UVICORN_RELOAD:-false}" = "true" ]; then
  set -- "$@" --reload
fi

exec "$@"
