#!/bin/sh

echo "📁 Creating database directory..."
mkdir -p /app/data

echo "🔄 Running migrations..."
alembic upgrade head

echo "🚀 Starting API..."
uvicorn app_gestao.main:app --host 0.0.0.0 --port 8000
