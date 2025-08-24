#!/bin/bash
# Docker entrypoint script for Document Manager

set -e

echo "🚀 Starting Document Manager..."

# Set OCR tool paths for Docker environment
export TESSERACT_PATH="/usr/bin/tesseract"
export POPPLER_PATH="/usr/bin"

# Ensure directories exist with correct permissions
echo "📁 Creating directories..."
mkdir -p /app/data /app/data/logs /app/data/staging /app/data/storage /app/data/uploads /app/data/backups

# Check required environment variables for production
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "MUST-BE-SET-IN-PRODUCTION" ]; then
        echo "⚠️  ERROR: SECRET_KEY must be set in production!"
        echo "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        exit 1
    fi
fi

if [ -z "$OPENAI_API_KEY" ] && [ "$AI_PROVIDER" = "openai" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set. AI features will be disabled."
fi

# Initialize database if needed
if [ ! -f "/app/data/documents.db" ]; then
    echo "🔧 Initializing database..."
    python -c "
from app.database import engine, Base
from app.models import *
print('Creating database tables...')
Base.metadata.create_all(bind=engine)
print('✅ Database initialized')
"
fi

# Check if any users exist
python -c "
from app.database import get_db
from app.models import User

db = next(get_db())
user_count = db.query(User).count()

if user_count == 0:
    print('ℹ️  No users found in database.')
    print('   Please create an administrator account through the web interface.')
else:
    print('✅ Found {} existing user(s) in database'.format(user_count))
db.close()
" || echo "⚠️  Warning: Could not check user count"

echo "✅ Initialization complete"

# Always run in all-in-one mode with embedded ChromaDB
echo "🔄 Starting in all-in-one mode with embedded ChromaDB..."
exec /app/docker-entrypoint-aio.sh