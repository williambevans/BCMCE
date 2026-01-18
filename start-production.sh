#!/bin/bash
# BCMCE Platform Production Startup Script
# HH Holdings LLC / Bevans Real Estate

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   BCMCE Platform - Production Deployment                      ║"
echo "║   HH Holdings LLC / Bevans Real Estate                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Production deployment requires configuration."
    echo "   Please create .env file with production settings."
    exit 1
fi

# Validate required environment variables
echo "🔍 Validating configuration..."
source .env

REQUIRED_VARS=(
    "DATABASE_URL"
    "REDIS_URL"
    "SECRET_KEY"
    "API_HOST"
    "API_PORT"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

echo "✅ Configuration validated!"
echo ""

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build --no-cache

# Start all services
echo "🚀 Starting production services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T postgres psql -U bcmce -d bcmce_db -f /docker-entrypoint-initdb.d/001_create_tables.sql

# Health check
echo "🏥 Performing health check..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy!"
        break
    fi
    echo "   Waiting for API... ($i/30)"
    sleep 2
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ BCMCE Platform is running in PRODUCTION mode!            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Access points:"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/api/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📋 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
