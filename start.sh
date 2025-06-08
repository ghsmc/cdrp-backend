#!/bin/bash

# Railway startup script
set -e

echo "Starting CDRP API deployment..."

# Set up Flask app
export FLASK_APP=app.py

echo "Running database migrations..."
flask db upgrade

echo "Seeding database..."
python scripts/seed_data.py

echo "Starting application..."
exec gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -