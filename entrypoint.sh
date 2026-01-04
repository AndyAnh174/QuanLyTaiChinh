#!/bin/sh

# Choose database host based on environment or default to 'db' service
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "Waiting for postgres at $DB_HOST:$DB_PORT..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server based on command passed or default to gunicorn
# If no arguments passed, start Gunicorn
if [ $# -eq 0 ]; then
    echo "Starting Gunicorn..."
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
    exec "$@"
fi
