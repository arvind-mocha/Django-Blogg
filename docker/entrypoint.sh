#!/bin/sh
set -eu
umask 077
mkdir -p "${DATA_DIR:-/app/data}/media"

# Management commands (tests, shell, createsuperuser) run without side effects.
if [ "${1:-}" = "gunicorn" ]; then
    python manage.py check
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
fi

exec "$@"
