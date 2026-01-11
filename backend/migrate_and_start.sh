#!/bin/bash

# Railway deployment script that runs migrations and starts the server
set -e

echo "🚀 Starting Garmin AI Coach Backend Deployment"

# Run database migrations
echo "📊 Running database migrations..."
python run_migrations.py --migrate

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed"
    exit 1
fi

# Start the FastAPI server
echo "🌐 Starting FastAPI server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}