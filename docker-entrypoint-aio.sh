#!/bin/bash
# All-in-One Docker entrypoint for Document Manager with embedded ChromaDB
set -e

echo "🚀 Starting All-in-One Document Manager..."
echo "📅 $(date)"
echo "🔧 Environment: ${ENVIRONMENT:-production}"

# Set OCR tool paths for Docker environment
export TESSERACT_PATH="/usr/bin/tesseract"
export POPPLER_PATH="/usr/bin"

# Create directories if needed
echo "📁 Creating directories..."
mkdir -p /app/data /app/data/logs /app/data/staging /app/data/storage /app/data/uploads /app/data/backups /app/data/chroma

# Check required environment variables for production
if [ "$ENVIRONMENT" = "production" ]; then
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "MUST-BE-SET-IN-PRODUCTION" ]; then
        echo "⚠️  ERROR: SECRET_KEY must be set in production!"
        echo "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
        exit 1
    fi
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

# Wait for ChromaDB to be ready (supervisor will start it)
echo "⏳ Starting services with supervisor..."

# Check if we're in development mode
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Development mode detected - enabling hot reload"
    # Copy supervisor config to writable location
    cp /etc/supervisor/conf.d/supervisord.conf /tmp/supervisord.conf
    # Update the copy to use reload flag
    sed -i 's|--port 8000|--port 8000 --reload|' /tmp/supervisord.conf
    # Use the modified config
    exec /usr/bin/supervisord -c /tmp/supervisord.conf
else
    # Start supervisor with original config
    exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi