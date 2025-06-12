#!/bin/bash

# Railway startup script
set -e

echo "Starting CDRP API deployment..."

# Set up Flask app
export FLASK_APP=app.py
export FLASK_ENV=production

# Check if we're in production with a database
if [ -n "$DATABASE_URL" ] || [ -n "$DATABASE_PRIVATE_URL" ]; then
    echo "Database found, running migrations..."
    
    # Try to run migrations, but don't fail if they don't work
    if flask db upgrade; then
        echo "Database migrations completed successfully"
        
        # Try to seed data if migrations worked
        if python scripts/seed_data.py; then
            echo "Database seeded successfully"
        else
            echo "Warning: Could not seed database, but continuing..."
        fi
    else
        echo "Warning: Database migrations failed, but continuing with existing schema..."
    fi
else
    echo "No database URL found, starting with SQLite fallback..."
    
    # Initialize database if it doesn't exist
    python -c "
from app import create_app
from app.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized')
"
    
    # Try to seed with fallback data
    python scripts/seed_data.py || echo "Could not seed data, but continuing..."
fi

echo "Starting application..."
# Use the PORT environment variable that Railway provides
exec gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -