#!/bin/sh
set -e

echo "Starting HairIQ Backend entrypoint script..."

# 1. Wait for PostgreSQL database
if [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
  until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        connect_timeout=3
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "PostgreSQL not ready, retrying in 2s..."
    sleep 2
  done
  echo "PostgreSQL is ready!"
fi

# 2. Apply database migrations
echo "Running migrations..."
python manage.py migrate --noinput --fake-initial

# 3. Ensure required directories exist
echo "Creating required directories..."
mkdir -p /app/media /app/staticfiles

# 4. Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# 5. Create superuser only if credentials are provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || echo "Superuser already exists or creation failed"
else
  echo "Skipping superuser creation - credentials not provided"
fi

echo "HairIQ Backend entrypoint completed successfully!"

# 6. Execute the CMD from Dockerfile
echo "Starting server..."
exec "$@"
