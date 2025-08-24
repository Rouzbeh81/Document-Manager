#!/bin/bash
# Document Manager Setup Script
# Usage: ./setup.sh [dev|prod|build|stop|status|logs]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Container name
CONTAINER_NAME="documentmanager"
IMAGE_NAME="documentmanager"

# Print colored output
print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Show usage
show_usage() {
    echo "Document Manager Setup Script"
    echo ""
    echo "Usage: ./setup.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev     - Start development environment with hot reload"
    echo "  prod    - Start production environment"
    echo "  build   - Build Docker image locally"
    echo "  stop    - Stop container"
    echo "  status  - Show container status"
    echo "  logs    - Show application logs"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./setup.sh dev          # Start development environment"
    echo "  ./setup.sh prod         # Start production environment"
    echo "  ./setup.sh build        # Build production image"
}

# Check requirements
check_requirements() {
    print_info "Checking requirements..."
    
    # Check for Docker or Podman
    if command -v podman &> /dev/null; then
        RUNTIME_CMD="podman"
        print_info "Using Podman"
    elif command -v docker &> /dev/null; then
        RUNTIME_CMD="docker"
        print_info "Using Docker"
    else
        print_error "Neither Docker nor Podman found. Please install one of them."
        exit 1
    fi
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        cat > .env << EOF
# Security - CHANGE THIS IN PRODUCTION!
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || echo "change-me-in-production")

# Database
DATABASE_URL=sqlite:///./data/documents.db

# AI Provider (optional)
AI_PROVIDER=openai
# OPENAI_API_KEY=your-key-here

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
        print_warn "Created .env file. Please update with your settings!"
    fi
}

# Load environment variables
load_env() {
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
}

# Development mode
start_dev() {
    print_info "Building development image..."
    $RUNTIME_CMD build -f Dockerfile.dev -t ${IMAGE_NAME}:dev .
    
    print_info "Starting development environment..."
    $RUNTIME_CMD run -d \
        --name ${CONTAINER_NAME}-dev \
        -p 8000:8000 \
        -v $(pwd)/app:/app/app:z \
        -v $(pwd)/frontend:/app/frontend:z \
        -v $(pwd)/data:/app/data:z \
        -v $(pwd)/staging:/app/staging:z \
        -v $(pwd)/storage:/app/storage:z \
        -v $(pwd)/uploads:/app/uploads:z \
        -v $(pwd)/logs:/app/logs:z \
        -v $(pwd)/backups:/app/backups:z \
        -v $(pwd)/chroma:/app/chroma:z \
        ${IMAGE_NAME}:dev
    
    print_info "Development environment started!"
    print_info "Access the application at http://localhost:8000"
}

# Production mode
start_prod() {
    print_info "Starting production environment..."
    create_env_file
    load_env
    
    # Check if SECRET_KEY is still default
    if [ "$SECRET_KEY" = "change-me-in-production" ]; then
        print_warn "Using default SECRET_KEY. Please change it for production!"
    fi
    
    # Always use local build for testing
    IMAGE="${IMAGE_NAME}:latest"
    if ! $RUNTIME_CMD image exists ${IMAGE} &>/dev/null; then
        print_error "Local image not found. Run './setup.sh build' first."
        exit 1
    fi
    
    $RUNTIME_CMD run -d \
        --name ${CONTAINER_NAME} \
        -p 8000:8000 \
        -e SECRET_KEY="${SECRET_KEY}" \
        -e DATABASE_URL="${DATABASE_URL}" \
        -e AI_PROVIDER="${AI_PROVIDER}" \
        -e OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
        -e ENVIRONMENT="${ENVIRONMENT}" \
        -e LOG_LEVEL="${LOG_LEVEL}" \
        -v $(pwd)/data:/app/data:z \
        -v $(pwd)/staging:/app/staging:z \
        -v $(pwd)/storage:/app/storage:z \
        -v $(pwd)/uploads:/app/uploads:z \
        -v $(pwd)/logs:/app/logs:z \
        -v $(pwd)/backups:/app/backups:z \
        -v $(pwd)/chroma:/app/chroma:z \
        --restart unless-stopped \
        $IMAGE
    
    print_info "Production environment started!"
    print_info "Access the application at http://localhost:8000"
}

# Build image
build_image() {
    print_info "Building production Docker image..."
    $RUNTIME_CMD build -t ${IMAGE_NAME}:latest .
    print_info "Build complete!"
}

# Stop containers
stop_containers() {
    print_info "Stopping containers..."
    
    # Stop dev container if running
    if $RUNTIME_CMD ps -a | grep -q ${CONTAINER_NAME}-dev; then
        $RUNTIME_CMD stop ${CONTAINER_NAME}-dev
        $RUNTIME_CMD rm ${CONTAINER_NAME}-dev
        print_info "Development container stopped and removed."
    fi
    
    # Stop prod container if running
    if $RUNTIME_CMD ps -a | grep -q ${CONTAINER_NAME}; then
        $RUNTIME_CMD stop ${CONTAINER_NAME}
        $RUNTIME_CMD rm ${CONTAINER_NAME}
        print_info "Production container stopped and removed."
    fi
}

# Show status
show_status() {
    print_info "Container status:"
    $RUNTIME_CMD ps -a | grep ${CONTAINER_NAME} || print_warn "No DocumentManager containers found."
}

# Show logs
show_logs() {
    # Check which container is running
    if $RUNTIME_CMD ps | grep -q ${CONTAINER_NAME}-dev; then
        $RUNTIME_CMD logs -f ${CONTAINER_NAME}-dev
    elif $RUNTIME_CMD ps | grep -q ${CONTAINER_NAME}; then
        $RUNTIME_CMD logs -f ${CONTAINER_NAME}
    else
        print_error "No running DocumentManager container found."
    fi
}

# Main execution
check_requirements

case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    build)
        build_image
        ;;
    stop)
        stop_containers
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac