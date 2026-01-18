#!/bin/bash
# BCMCE Platform Development Startup Script
# HH Holdings LLC / Bevans Real Estate

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   BCMCE Platform - Development Environment                    ║"
echo "║   HH Holdings LLC / Bevans Real Estate                        ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if database is initialized
echo "🗄️  Checking database..."
docker-compose exec -T postgres psql -U bcmce -d bcmce_db -c "SELECT 1" > /dev/null 2>&1 || {
    echo "📊 Initializing database..."
    docker-compose exec -T postgres psql -U bcmce -d bcmce_db -f /docker-entrypoint-initdb.d/001_create_tables.sql
    echo "✅ Database initialized!"
}

echo ""
echo "📦 Installing Python dependencies..."
cd backend
pip install -q -r requirements.txt
cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Development environment ready!                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Services:"
echo "   PostgreSQL:  localhost:5432"
echo "   Redis:       localhost:6379"
echo ""
echo "📋 Next steps:"
echo "   1. Run: cd backend && python main.py"
echo "   2. Open: http://localhost:8000/api/docs"
echo "   3. View frontend: Open index.html in browser"
echo ""
echo "💡 Useful commands:"
echo "   make dev          - Start backend API server"
echo "   make test         - Run tests"
echo "   make docker-down  - Stop all services"
echo ""
