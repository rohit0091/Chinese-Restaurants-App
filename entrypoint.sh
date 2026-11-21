#!/bin/sh
set -e

# Apply database migrations
python manage.py migrate --noinput

# Seed database with initial categories and menu items
if [ -f data.json ]; then
    python manage.py loaddata data.json 2>/dev/null || true
fi

# Start Gunicorn server
exec gunicorn MahatoChineseCenter.wsgi:application \
    --bind 0.0.0.0:5000 \
    --workers 1 \
    --threads 4 \
    --timeout 30
