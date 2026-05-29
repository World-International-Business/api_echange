#!/bin/sh
set -e

echo "=== Applying migrations ==="
python manage.py migrate --settings=forex_platform.settings --noinput

echo "=== Loading currencies fixture ==="
python manage.py loaddata currencies --settings=forex_platform.settings 2>/dev/null || true

echo "=== Starting services ==="
exec "$@"
