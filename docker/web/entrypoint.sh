#!/usr/bin/env sh
set -e

# espera o Postgres
until nc -z db 5432; do
  echo "Aguardando Postgres..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# inicia gunicorn, garantindo que ele aceite conexões externas (de outros containers)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
